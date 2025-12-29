/**
 * ShipCard Component
 * Displays recommended ship information
 */

export function ShipCard({ ship }) {
  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-blue-500 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-lg font-bold text-white">{ship.ship_name}</h3>
          <p className="text-sm text-gray-400">{ship.manufacturer}</p>
        </div>
        {ship.priority && (
          <span className="px-2 py-1 bg-blue-600 text-white text-xs font-bold rounded">
            #{ship.priority}
          </span>
        )}
      </div>

      {ship.recommendation_reason && (
        <p className="text-sm text-gray-300 mb-3">
          {ship.recommendation_reason}
        </p>
      )}

      <div className="grid grid-cols-2 gap-2 text-sm">
        {ship.focus && (
          <div>
            <span className="text-gray-500">Role:</span>
            <span className="text-gray-200 ml-2">{ship.focus}</span>
          </div>
        )}

        {ship.cargo_capacity !== undefined && (
          <div>
            <span className="text-gray-500">Cargo:</span>
            <span className="text-gray-200 ml-2">{ship.cargo_capacity} SCU</span>
          </div>
        )}

        {ship.crew_min !== undefined && (
          <div>
            <span className="text-gray-500">Crew:</span>
            <span className="text-gray-200 ml-2">{ship.crew_min}+</span>
          </div>
        )}

        {ship.price_usd && (
          <div>
            <span className="text-gray-500">Price:</span>
            <span className="text-green-400 ml-2 font-semibold">${ship.price_usd}</span>
          </div>
        )}
      </div>

      {ship.slug && (
        <a
          href={`https://starcitizen.tools/${ship.slug}`}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-3 inline-block text-blue-400 hover:text-blue-300 text-sm"
        >
          Learn more →
        </a>
      )}
    </div>
  );
}

export default ShipCard;
