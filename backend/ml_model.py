import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
import shutil
import tempfile
from datetime import datetime
import matplotlib.pyplot as plt

from data_pipeline import load_and_clean_data

FEATURE_COLUMNS = [
    'latitude', 'longitude',
    'hour_of_day', 'day_of_week', 'is_weekend',
    'event_cause', 'veh_type', 'corridor', 'corridor_priority',
    'requires_road_closure', 'event_type', 'police_station',
    'has_severity_keyword', 'resolution_time_minutes'
]

_SEVERITY_KEYWORDS = ['severe', 'fatal', 'fire', 'water', 'heavy', 'blast', 'accident', 'dead', 'injur']
_PRIORITY_MAP = {'Low': 1, 'Medium': 2, 'High': 3}

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

ML_OUTPUT_PATH = os.path.join(
    PROJECT_ROOT,
    "ml"
)

DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "dataset.csv"
)


def save_feature_importance(clf):
    """
    Extracts feature importance from Gradient Boosting model
    after preprocessing and saves visualization.
    """

    # Get trained Gradient Boosting model
    model = clf.named_steps['model']

    # Get preprocessing pipeline
    preprocessor = clf.named_steps['preprocessor']

    # Get transformed feature names after encoding
    feature_names = preprocessor.get_feature_names_out()

    # Get importance values
    importance = model.feature_importances_

    # Create dataframe
    feature_importance = pd.DataFrame({
        "Feature": feature_names,
        "Importance": importance
    })

    # Sort by importance
    feature_importance = feature_importance.sort_values(
        by="Importance",
        ascending=False
    )

    print("\nTop Important Features:")
    print(feature_importance.head(15))


    # Save CSV
    feature_importance.to_csv(
    os.path.join(
        ML_OUTPUT_PATH,
        "feature_importance.csv"
    ),
    index=False
)


    # Plot top 15 features
    top_features = feature_importance.head(15)

    plt.figure(figsize=(10, 6))

    plt.barh(
        top_features["Feature"],
        top_features["Importance"]
    )

    plt.xlabel("Importance Score")
    plt.ylabel("Feature")
    plt.title("Traffic Prediction Feature Importance")

    plt.gca().invert_yaxis()

    plt.tight_layout()

    plt.savefig(
    os.path.join(
        ML_OUTPUT_PATH,
        "feature_importance.png"
    ),
    dpi=300
)

    plt.close()

    print("Feature importance visualization saved.")



MODEL_PATH = os.path.join(
    ML_OUTPUT_PATH,
    "model.joblib"
)

def _feedback_rows_to_dataframe(feedback_rows: list[dict]) -> pd.DataFrame:
    """
    Converts resolved-deployment rows straight from the database into the
    same feature schema produced by data_pipeline.load_and_clean_data(), so
    they can be concatenated onto the base dataset for training. No file I/O
    happens here — this is the in-memory replacement for appending rows to
    dataset.csv.
    """
    records = []
    for row in feedback_rows:
        try:
            dt = datetime.fromisoformat(str(row.get('time', '')).replace("Z", "+00:00"))
        except (ValueError, TypeError):
            dt = datetime.now()

        duration = row.get('actual_duration')
        if duration is None or duration <= 0 or duration >= 1440:
            continue  # same sanity bounds load_and_clean_data applies

        description = (row.get('description') or '').lower()
        priority = row.get('priority') or 'Low'

        records.append({
            'latitude': row.get('latitude', 0.0),
            'longitude': row.get('longitude', 0.0),
            'hour_of_day': dt.hour,
            'day_of_week': dt.weekday(),
            'is_weekend': 1 if dt.weekday() in (5, 6) else 0,
            'event_cause': row.get('event_cause') or 'unknown',
            'veh_type': row.get('veh_type') or 'unknown',
            'corridor': row.get('corridor') or 'Non-corridor',
            'corridor_priority': _PRIORITY_MAP.get(priority, 1),
            'requires_road_closure': int(bool(row.get('requires_road_closure'))),
            'event_type': row.get('event_type') or 'unknown',
            'police_station': row.get('police_station') or 'unknown',
            'has_severity_keyword': 1 if any(kw in description for kw in _SEVERITY_KEYWORDS) else 0,
            'resolution_time_minutes': float(duration),
        })

    if not records:
        return pd.DataFrame(columns=FEATURE_COLUMNS)
    return pd.DataFrame.from_records(records)[FEATURE_COLUMNS]


def build_training_dataframe(data_path: str = DATA_PATH, feedback_rows: list[dict] | None = None) -> pd.DataFrame:
    """
    Combines the base historical dataset with any resolved-deployment
    feedback pulled from the database (issue #41: feedback now lives in
    Postgres/SQLite, not dataset.csv, so it survives redeploys and there's
    no concurrent-write race on a shared CSV file).
    """
    base_df = load_and_clean_data(data_path)
    if feedback_rows:
        feedback_df = _feedback_rows_to_dataframe(feedback_rows)
        if not feedback_df.empty:
            base_df = pd.concat([base_df, feedback_df], ignore_index=True)
    return base_df


def _build_pipeline() -> Pipeline:
    categorical_features = [
        'event_cause', 'veh_type', 'corridor', 'event_type', 'police_station'
    ]
    numerical_features = [
        'latitude', 'longitude', 'hour_of_day', 'day_of_week', 'is_weekend',
        'corridor_priority', 'requires_road_closure', 'has_severity_keyword'
    ]
    preprocessor = ColumnTransformer(transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
    ])
    model = GradientBoostingRegressor(
        n_estimators=300, learning_rate=0.05, max_depth=5,
        subsample=0.8, random_state=42,
    )
    return Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])


def evaluate_model(clf, X_test: pd.DataFrame, y_test: pd.Series) -> tuple[float, float]:
    """Returns (MAE, R²) for a fitted pipeline on a held-out test set."""
    y_pred = clf.predict(X_test)
    return (
        float(mean_absolute_error(y_test, y_pred)),
        float(r2_score(y_test, y_pred)),
    )


def train_and_save_model(
    data_path: str = DATA_PATH,
    model_save_path: str = MODEL_PATH
):

    print("Loading and cleaning data...")

    df = load_and_clean_data(data_path)

    print(f"Training data: {df.shape[0]} rows")


    X = df.drop(columns=['resolution_time_minutes'])
    y = df['resolution_time_minutes']


    categorical_features = [
        'event_cause',
        'veh_type',
        'corridor',
        'event_type',
        'police_station'
    ]


    numerical_features = [
        'latitude',
        'longitude',
        'hour_of_day',
        'day_of_week',
        'is_weekend',
        'corridor_priority',
        'requires_road_closure',
        'has_severity_keyword'
    ]


    preprocessor = ColumnTransformer(
        transformers=[
            (
                'num',
                StandardScaler(),
                numerical_features
            ),
            (
                'cat',
                OneHotEncoder(handle_unknown='ignore'),
                categorical_features
            ),
        ]
    )


    model = GradientBoostingRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        random_state=42
    )


    clf = Pipeline(
        steps=[
            ('preprocessor', preprocessor),
            ('model', model)
        ]
    )


    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )


    print("Training model (GradientBoostingRegressor)...")

    clf.fit(
        X_train,
        y_train
    )


    # NEW FEATURE:
    # Generate feature importance after training
    save_feature_importance(clf)



    y_pred = clf.predict(X_test)


    mae = mean_absolute_error(
        y_test,
        y_pred
    )

    r2 = r2_score(
        y_test,
        y_pred
    )


    print(
        f"MAE: {mae:.1f} minutes | R²: {r2:.3f}"
    )


    joblib.dump(
        clf,
        model_save_path
    )


    print(
        f"Model saved to {model_save_path}"
    )



def rollback_model(model_path: str = 'model.joblib') -> bool:
    """
    Restores the previous production model from its backup. Used when a
    promoted model turns out to be bad in practice and needs to be undone
    without a redeploy.
    """
    backup_path = model_path + '.previous'
    if not os.path.exists(backup_path):
        print(f"No backup found at {backup_path}; cannot roll back.")
        return False
    shutil.copyfile(backup_path, model_path)
    print(f"Rolled back {model_path} from {backup_path}.")
    return True


def run_validated_retraining(
    feedback_rows: list[dict],
    data_path: str = DATA_PATH,
    model_save_path: str = 'model.joblib',
    mae_tolerance: float = 0.05,   # candidate may be up to 5% worse on MAE...
    r2_tolerance: float = 0.02,    # ...and up to 0.02 worse on R², and still promote
) -> dict:
    """
    Retrains a candidate model from the base dataset plus DB-backed feedback,
    evaluates it against the currently-deployed model on a shared held-out
    test split, and only promotes it if it isn't meaningfully worse.

    This never touches dataset.csv — training data is assembled entirely in
    memory from the base CSV (static, read-only) and feedback fetched from
    the database — so there's no concurrent-write race and nothing is lost
    on ephemeral storage. Returns a dict describing what happened, suitable
    for storing on a retrain_jobs row.
    """
    result = {
        "status": "failed",
        "message": "",
        "baseline_mae": None, "baseline_r2": None,
        "candidate_mae": None, "candidate_r2": None,
        "promoted": False,
    }

    try:
        df = build_training_dataframe(data_path=data_path, feedback_rows=feedback_rows)
        X = df.drop(columns=['resolution_time_minutes'])
        y = df['resolution_time_minutes']

        # Fixed random_state -> baseline and candidate are compared on the
        # exact same held-out rows.
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        candidate = _build_pipeline()
        candidate.fit(X_train, y_train)
        candidate_mae, candidate_r2 = evaluate_model(candidate, X_test, y_test)
        result["candidate_mae"], result["candidate_r2"] = candidate_mae, candidate_r2
        print(f"Candidate model — MAE: {candidate_mae:.2f} | R²: {candidate_r2:.3f}")

        baseline_mae, baseline_r2 = None, None
        if os.path.exists(model_save_path):
            try:
                current = joblib.load(model_save_path)
                baseline_mae, baseline_r2 = evaluate_model(current, X_test, y_test)
                result["baseline_mae"], result["baseline_r2"] = baseline_mae, baseline_r2
                print(f"Current model  — MAE: {baseline_mae:.2f} | R²: {baseline_r2:.3f}")
            except Exception as e:
                print("Could not evaluate current production model (treating as no baseline):", e)

        should_promote = (
            baseline_mae is None
            or (
                candidate_mae <= baseline_mae * (1 + mae_tolerance)
                and candidate_r2 >= baseline_r2 - r2_tolerance
            )
        )

        if not should_promote:
            result["status"] = "rejected"
            result["message"] = (
                f"Candidate did not beat current model within tolerance "
                f"(MAE {candidate_mae:.2f} vs {baseline_mae:.2f}, "
                f"R² {candidate_r2:.3f} vs {baseline_r2:.3f}); keeping existing model."
            )
            print(result["message"])
            return result

        # Promote atomically: write to a temp file in the same directory,
        # back up the current model, then os.replace() the live file. This
        # avoids anyone (including another request handler reading the
        # model to serve a prediction) ever seeing a partially-written file.
        target_dir = os.path.dirname(os.path.abspath(model_save_path)) or "."
        fd, tmp_path = tempfile.mkstemp(dir=target_dir, suffix=".joblib.tmp")
        os.close(fd)
        try:
            joblib.dump(candidate, tmp_path)
            if os.path.exists(model_save_path):
                shutil.copyfile(model_save_path, model_save_path + '.previous')
            os.replace(tmp_path, model_save_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        result["status"] = "promoted"
        result["promoted"] = True
        result["message"] = "New model promoted to production."
        print(result["message"])
        return result

    except Exception as e:
        result["status"] = "failed"
        result["message"] = f"Retraining failed: {e}"
        print(result["message"])
        return result


if __name__ == "__main__":
    train_and_save_model()