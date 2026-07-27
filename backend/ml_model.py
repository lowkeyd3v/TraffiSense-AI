import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
import matplotlib.pyplot as plt

from data_pipeline import load_and_clean_data

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



def train_and_save_model(
    data_path: str = DATA_PATH,
    model_save_path: str = 'model.joblib'
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



def retrain_with_feedback(
    feedback_row: dict,
    data_path: str = DATA_PATH,
    model_save_path: str = 'model.joblib'
):

    """
    Appends a resolved deployment row to dataset.csv
    and retrains the model.
    """

    print(
        f"Online retraining triggered with feedback_row: {feedback_row}"
    )


    try:
        from datetime import datetime, timedelta

        start_dt = datetime.fromisoformat(
            feedback_row['time'].replace("Z", "+00:00")
        )

        duration_mins = float(
            feedback_row['actual_duration']
        )

        closed_dt = start_dt + timedelta(
            minutes=duration_mins
        )

        start_str = start_dt.strftime(
            '%Y-%m-%d %H:%M:%S+00:00'
        )

        closed_str = closed_dt.strftime(
            '%Y-%m-%d %H:%M:%S+00:00'
        )

    except Exception as e:

        print(
            "Error parsing datetime:",
            e
        )

        start_str = datetime.utcnow().strftime(
            '%Y-%m-%d %H:%M:%S+00:00'
        )

        closed_str = start_str



    new_csv_row = {
        'start_datetime': start_str,
        'closed_datetime': closed_str,
        'event_cause': feedback_row.get('event_cause', 'unknown'),
        'veh_type': feedback_row.get('veh_type', 'unknown'),
        'corridor': feedback_row.get('corridor', 'Non-corridor'),
        'priority': feedback_row.get('priority', 'Low'),
        'requires_road_closure': 'True' if feedback_row.get('requires_road_closure') else 'False',
        'event_type': feedback_row.get('event_type', 'unknown'),
        'latitude': feedback_row.get('latitude', 0.0),
        'longitude': feedback_row.get('longitude', 0.0),
        'police_station': feedback_row.get('police_station', 'unknown'),
        'description': feedback_row.get('description', ''),
        'zone': 'unknown',
        'junction': 'unknown',
        'endlatitude': feedback_row.get('latitude', 0.0),
        'endlongitude': feedback_row.get('longitude', 0.0)
    }


    try:

        new_df = pd.DataFrame(
            [new_csv_row]
        )

        new_df.to_csv(
            data_path,
            mode='a',
            header=False,
            index=False
        )

        print(
            "Successfully appended feedback row"
        )


    except Exception as e:

        print(
            "Failed to append:",
            e
        )


    try:

        train_and_save_model(
            data_path=data_path,
            model_save_path=model_save_path
        )

        print(
            "Online retraining completed successfully."
        )

        return True


    except Exception as e:

        print(
            "Retraining failed:",
            e
        )

        return False



if __name__ == "__main__":
    train_and_save_model()