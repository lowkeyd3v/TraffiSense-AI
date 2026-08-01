import React from 'react';

const SIMULATED_FEEDS = [
  {
    id: 1,
    title: "Chinnaswamy Stadium Cricket Match",
    source: "BookMyShow API (Simulated)",
    time: "Today, 19:30 IST",
    tags: ["High Traffic", "Planned Event"],
    formData: {
      event_type: 'planned',
      event_cause: 'procession',
      corridor: 'MG Road',
      priority: 'High',
      veh_type: 'others',
      latitude: 12.9788,
      longitude: 77.5996,
      police_station: 'Cubbon Park',
      event_scale: 'Large',
      crowd_size: 35000,
      requires_road_closure: true,
      description: "IPL T20 Cricket Match. Expect heavy footfall and parking spillover around Queens Road and MG Road.",
    },
    desc: "IPL T20 Cricket Match. Expect heavy footfall and parking spillover around Queens Road and MG Road."
  },
  {
    id: 2,
    title: "Political Rally at Freedom Park",
    source: "News/Social Scraper (Simulated)",
    time: "Tomorrow, 10:00 IST",
    tags: ["Protest", "Planned Event"],
    formData: {
      event_type: 'planned',
      event_cause: 'procession',
      corridor: 'Seshadri Road',
      priority: 'High',
      veh_type: 'others',
      latitude: 12.9772,
      longitude: 77.5806,
      police_station: 'Upparpet',
      event_scale: 'Large',
      crowd_size: 15000,
      requires_road_closure: true,
      description: "Scheduled political gathering. High likelihood of slow-moving traffic towards Anand Rao Circle.",
    },
    desc: "Scheduled political gathering. High likelihood of slow-moving traffic towards Anand Rao Circle."
  },
  {
    id: 3,
    title: "Heavy Rains Alert - Underpass Flooding",
    source: "KSNDMC Weather API (Simulated)",
    time: "Live - Ongoing",
    tags: ["Weather Warning", "Unplanned Event"],
    formData: {
      event_type: 'unplanned',
      event_cause: 'water_logging',
      corridor: 'ORR Marathahalli',
      priority: 'High',
      veh_type: 'unknown',
      latitude: 12.9569,
      longitude: 77.7011,
      police_station: 'Marathahalli',
      event_scale: 'Medium',
      crowd_size: 0,
      requires_road_closure: true,
      description: "Sudden downpour causing significant waterlogging at Bellandur underpass. Traffic diverted.",
    },
    desc: "Sudden downpour causing significant waterlogging at Bellandur underpass. Traffic diverted."
  }
];

export default function LiveFeeds({ onEventSelect, onBack }) {
  return (
    <div className="min-h-screen bg-white flex flex-col font-sans">
      
      <div className="max-w-6xl mx-auto w-full p-8 mt-8 fade-in-up">
        {/* Header Section */}
        <div className="mb-12 flex flex-col items-center text-center">
          <div className="flex items-center gap-3 text-xs font-bold text-gray-400 uppercase tracking-widest mb-8 border border-gray-200 px-4 py-2 rounded-full shadow-sm">
            <span className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span> LIVE SIMULATION</span>
            <span>·</span>
            <span>API AGGREGATOR</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-black text-gray-900 tracking-tight mb-6">
            Live Event <span className="text-fk-blue">Feeds</span>
          </h1>
          <p className="text-gray-500 font-medium text-xl max-w-3xl">
            Aggregating data from ticketing platforms, weather APIs, and social media to predict planned and unplanned congestion before it hits the grid.
          </p>
        </div>

        {/* Feed Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {SIMULATED_FEEDS.map((feed, idx) => (
            <div key={feed.id} className="bg-white rounded-[2rem] border border-gray-200 overflow-hidden hover:-translate-y-2 transition-transform duration-300 flex flex-col shadow-sm hover:shadow-2xl group cursor-pointer" style={{animationDelay: `${idx * 0.1}s`}}>
              <div className="p-8 flex-1 flex flex-col">
                <div className="text-xs font-extrabold text-fk-blue uppercase tracking-widest mb-4">
                  {feed.source}
                </div>
                
                <h3 className="font-black text-3xl text-gray-900 leading-tight mb-4">{feed.title}</h3>
                
                <div className="flex items-center gap-2 mb-6">
                   <span className="text-xs font-bold text-gray-600 bg-gray-100 px-3 py-1.5 rounded-full whitespace-nowrap">
                    {feed.time}
                  </span>
                </div>
                
                <div className="flex flex-wrap gap-2 mb-6">
                  {feed.tags.map(tag => (
                    <span key={tag} className="text-xs font-bold px-3 py-1 rounded-full bg-blue-50 text-fk-blue border border-blue-100">
                      {tag}
                    </span>
                  ))}
                </div>

                <p className="text-gray-500 mb-8 leading-relaxed flex-1 font-medium text-lg">
                  {feed.desc}
                </p>

                <button 
                  onClick={() => onEventSelect(feed.formData)}
                  className="w-full py-4 bg-fk-yellow hover:bg-yellow-400 text-gray-900 font-black text-lg rounded-xl transition-all flex items-center justify-center gap-2 group shadow-sm hover:shadow-md"
                >
                  Analyze Impact <span>→</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
