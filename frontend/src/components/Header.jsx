import React, { useState } from "react";

export default function Header({ setView }) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>
      <header className="bg-white border-b border-gray-100 flex flex-col lg:flex-row items-center justify-between gap-4 px-4 sm:px-6 lg:px-8 py-4 sticky top-0 z-50">
        <div
          className="flex items-center gap-3 cursor-pointer self-start lg:self-auto"
          onClick={() => setView && setView("landing")}
        >
          <div className="w-9 h-9 bg-fk-yellow text-fk-blue rounded-lg flex items-center justify-center font-extrabold text-xl shadow-sm">
            Ts
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-xl sm:text-2xl font-black tracking-tight text-gray-900 leading-none">
              TraffiSense
            </span>
            <span className="text-xl sm:text-2xl font-black tracking-tight text-fk-blue leading-none">
              AI
            </span>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-center gap-3 sm:gap-6 w-full lg:w-auto">
          <nav className="hidden md:flex items-center gap-2 lg:gap-4 text-sm font-bold text-gray-500">
            <button
              onClick={() => setIsModalOpen(true)}
              className="hover:text-fk-blue transition-colors px-3 py-1.5 rounded-full hover:bg-blue-50"
            >
              ℹ️ Features
            </button>
            <a
              href="https://github.com/lowkeyd3v/TraffiSense-AI"
              target="_blank"
              rel="noreferrer"
              className="hover:text-gray-900 transition-colors flex items-center gap-1.5 px-3 py-1.5 rounded-full hover:bg-gray-100"
            >
              <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current">
                <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" />
              </svg>
              GitHub
            </a>
          </nav>

          <div className="flex flex-col sm:flex-row items-center gap-3 w-full sm:w-auto">
            {setView && (
              <button
                onClick={() => setView("live_feeds")}
                className="w-full sm:w-auto justify-center bg-red-500 hover:bg-red-600 text-white px-5 py-2 rounded-full text-sm font-extrabold shadow-sm transition-all flex items-center gap-2"
              >
                <div className="w-2 h-2 rounded-full bg-white animate-ping" />
                Live Feed
              </button>
            )}
            <div className="w-full sm:w-auto justify-center bg-fk-blue text-white px-5 py-2 rounded-full text-sm font-extrabold shadow-md flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              SYSTEM ONLINE
            </div>
          </div>
        </div>
      </header>

      {/* Features Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-5 sm:p-8 relative">
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-full bg-gray-100 hover:bg-gray-200 text-gray-600 transition-colors"
            >
              ✕
            </button>
            <h2 className="text-2xl font-black text-gray-900 mb-6 flex items-center gap-3">
              <span className="text-3xl">✨</span> Platform Features
            </h2>

            <div className="space-y-6 text-gray-700">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="w-12 h-12 shrink-0 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center text-xl font-bold">
                  🤖
                </div>
                <div>
                  <h3 className="font-bold text-gray-900 text-lg mb-1">
                    AI Congestion Prediction
                  </h3>
                  <p className="text-sm">
                    Gradient Boosting Regressor ML model trained to predict clearance times
                    and road closures based on event parameters.
                  </p>
                </div>
              </div>
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="w-12 h-12 shrink-0 bg-yellow-50 text-yellow-600 rounded-xl flex items-center justify-center text-xl font-bold">
                  🗺️
                </div>
                <div>
                  <h3 className="font-bold text-gray-900 text-lg mb-1">
                    Dynamic Mappls Diversion
                  </h3>
                  <p className="text-sm">
                    Generates real-time map routes visually blocking the
                    affected corridor and suggesting primary and alternative
                    diversions.
                  </p>
                </div>
              </div>
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="w-12 h-12 shrink-0 bg-red-50 text-red-600 rounded-xl flex items-center justify-center text-xl font-bold">
                  📡
                </div>
                <div>
                  <h3 className="font-bold text-gray-900 text-lg mb-1">
                    Live Feed Integration
                  </h3>
                  <p className="text-sm">
                    Simulated aggregation of API sources (BookMyShow, Weather,
                    Twitter) to automatically flag pre-planned and unplanned
                    incidents.
                  </p>
                </div>
              </div>
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="w-12 h-12 shrink-0 bg-purple-50 text-purple-600 rounded-xl flex items-center justify-center text-xl font-bold">
                  📱
                </div>
                <div>
                  <h3 className="font-bold text-gray-900 text-lg mb-1">
                    Automated WhatsApp Alerts
                  </h3>
                  <p className="text-sm">
                    One-click generation of public advisories ready to be
                    broadcasted to commuters over WhatsApp or Twitter.
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-8 pt-4 border-t flex justify-end">
              <button
                onClick={() => setIsModalOpen(false)}
                className="px-6 py-2 bg-fk-blue text-white font-bold rounded-lg hover:bg-blue-700"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
