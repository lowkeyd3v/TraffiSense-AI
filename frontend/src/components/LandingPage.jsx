import React from 'react';

export default function LandingPage({ onScenarioSelect, onLiveFeedSelect }) {
  return (
    <div className="flex flex-col lg:flex-row min-h-screen">

      {/* Left Side: Content & Scenarios */}
      <div className="flex-1 p-5 sm:p-8 lg:p-16 flex flex-col items-start fade-in-up">

        <h1 className="text-4xl sm:text-5xl lg:text-7xl font-black text-gray-900 tracking-tight leading-tight mb-6 max-w-xl">
          Making India <span className="text-fk-blue">move smarter</span>
        </h1>

        <p className="text-base sm:text-lg lg:text-xl text-gray-500 font-medium max-w-xl mb-10 lg:mb-12 leading-relaxed">
          Simulate real-world traffic incidents and use AI-powered predictions to manage congestion, emergencies, and urban mobility.
        </p>


        {/* Scenario Cards */}
        <div className="flex flex-col gap-4 sm:gap-6 w-full max-w-xl">


          {/* Scenario 1 */}
          <div
            onClick={() => onScenarioSelect('water_logging')}
            className="group cursor-pointer bg-white border border-gray-200 rounded-2xl p-4 sm:p-6 shadow-sm hover:shadow-xl transition-all w-full flex flex-col sm:flex-row items-start gap-4 sm:gap-6"
          >
            <div className="w-14 h-14 sm:w-16 sm:h-16 shrink-0 bg-blue-50 text-fk-blue rounded-full flex items-center justify-center text-3xl group-hover:scale-110 transition-transform">
              🌊
            </div>

            <div>
              <div className="text-[0.65rem] font-black text-fk-blue uppercase tracking-widest mb-1">
                SCENARIO 1
              </div>

              <h3 className="text-lg sm:text-xl font-black text-gray-900 mb-1">
                Urban Flooding
              </h3>

              <p className="text-gray-500 font-medium text-sm mb-4">
                Mumbai Monsoon Zone / Bengaluru Underpass
              </p>

              <ul className="text-xs text-gray-600 space-y-2 font-medium">
                <li className="flex gap-2">
                  <span className="font-bold text-gray-900">1</span>
                  Predict waterlogging clearance time using AI models.
                </li>

                <li className="flex gap-2">
                  <span className="font-bold text-gray-900">2</span>
                  Recommend drainage, pumping, and diversion plans.
                </li>

                <li className="flex gap-2">
                  <span className="font-bold text-gray-900">3</span>
                  Estimate impact on nearby roads and transport.
                </li>
              </ul>
            </div>
          </div>



          {/* Scenario 2 */}
          <div
            onClick={() => onScenarioSelect('accident')}
            className="group cursor-pointer bg-white border border-gray-200 rounded-2xl p-4 sm:p-6 shadow-sm hover:shadow-xl transition-all w-full flex flex-col sm:flex-row items-start gap-4 sm:gap-6"
          >
            <div className="w-14 h-14 sm:w-16 sm:h-16 shrink-0 bg-red-50 text-red-500 rounded-full flex items-center justify-center text-3xl group-hover:scale-110 transition-transform">
              🚑
            </div>

            <div>
              <div className="text-[0.65rem] font-black text-red-500 uppercase tracking-widest mb-1">
                SCENARIO 2
              </div>

              <h3 className="text-lg sm:text-xl font-black text-gray-900 mb-1">
                Highway Accident Response
              </h3>

              <p className="text-gray-500 font-medium text-sm mb-4">
                Delhi–Mumbai Expressway / Bengaluru Ring Road
              </p>

              <ul className="text-xs text-gray-600 space-y-2 font-medium">
                <li className="flex gap-2">
                  <span className="font-bold text-gray-900">1</span>
                  Analyze accident severity and congestion spread.
                </li>

                <li className="flex gap-2">
                  <span className="font-bold text-gray-900">2</span>
                  Generate alternate route recommendations.
                </li>

                <li className="flex gap-2">
                  <span className="font-bold text-gray-900">3</span>
                  Predict traffic recovery time after response.
                </li>
              </ul>
            </div>
          </div>



          {/* Scenario 3 */}
          <div
            onClick={() => onScenarioSelect('vip_movement')}
            className="group cursor-pointer bg-white border border-gray-200 rounded-2xl p-4 sm:p-6 shadow-sm hover:shadow-xl transition-all w-full flex flex-col sm:flex-row items-start gap-4 sm:gap-6"
          >
            <div className="w-14 h-14 sm:w-16 sm:h-16 shrink-0 bg-yellow-50 text-yellow-600 rounded-full flex into-center justify-center text-3xl group-hover:scale-110 transition-transform">
              🚔
            </div>

            <div>
              <div className="text-[0.65rem] font-black text-yellow-600 uppercase tracking-widest mb-1">
                SCENARIO 3
              </div>

              <h3 className="text-lg sm:text-xl font-black text-gray-900 mb-1">
                VIP Convoy Management
              </h3>

              <p className="text-gray-500 font-medium text-sm mb-4">
                Delhi Central Roads / Airport Corridors
              </p>

              <ul className="text-xs text-gray-600 space-y-2 font-medium">
                <li className="flex gap-2">
                  <span className="font-bold text-gray-900">1</span>
                  Simulate temporary road closures.
                </li>

                <li className="flex gap-2">
                  <span className="font-bold text-gray-900">2</span>
                  Forecast congestion hotspots and delays.
                </li>

                <li className="flex gap-2">
                  <span className="font-bold text-gray-900">3</span>
                  Optimize traffic personnel deployment.
                </li>
              </ul>
            </div>
          </div>


        </div>
      </div>



      {/* Right Side */}
      <div
        className="flex-1 p-5 sm:p-8 lg:p-16 flex items-center justify-center bg-gray-50 lg:border-l border-gray-100 fade-in-up"
        style={{ animationDelay: '0.1s' }}
      >

        <div className="bg-fk-blue rounded-3xl lg:rounded-[2.5rem] p-6 sm:p-8 lg:p-12 text-center flex flex-col items-center shadow-2xl w-full max-w-xl relative overflow-hidden">

          <div className="text-xs font-black text-blue-200 uppercase tracking-widest mb-10">
            TRAFFISENSE AI CONTROL CENTER
          </div>


          <button
            onClick={onLiveFeedSelect}
            className="w-full sm:w-auto bg-fk-yellow hover:bg-yellow-400 text-gray-900 px-6 sm:px-8 py-3 sm:py-4 rounded-full font-black text-lg sm:text-xl shadow-xl hover:scale-105 transition-all flex items-center justify-center gap-3 mb-8 sm:mb-10"
          >
            Launch Live Traffic Feeds →
          </button>


          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black text-white tracking-tight leading-tight mb-8">
            Predict congestion. Manage incidents. Build smarter Indian cities.
          </h2>


          <p className="text-blue-200 font-medium text-sm opacity-80">
            AI Predictions · Real-time Events · Smart Routing · Traffic Intelligence
          </p>

        </div>

      </div>

    </div>
  );
}