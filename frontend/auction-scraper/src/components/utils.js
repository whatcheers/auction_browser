// Endpoints for different auction sources
const endpoints = {
  'Ending Today': 'http://hashbrowns/bin/ending-today.php',
  'GovDeals': 'http://hashbrowns/bin/govdeals-locations.php',
  'Wisconsin Surplus': 'http://hashbrowns/bin/wisco-locations.php',
  'HiBid': 'http://hashbrowns/bin/hibid-locations.php',
  'Public Surplus': 'http://hashbrowns/bin/publicsurplus-locations.php',
  'GSA': 'http://hashbrowns/bin/gsa-locations.php',
  'Backes': 'http://hashbrowns/bin/backes-locations.php',
  'Bidspotter': 'http://hashbrowns/bin/bidspotter-locations.php',
  'SMC': 'http://hashbrowns/bin/smc-locations.php',
  'Heartland': 'http://hashbrowns/bin/heartland-locations.php',
  'Proxibid': 'http://hashbrowns/bin/proxibid-locations.php', 
};

// Mapping of auction sources to their respective database table names
const tableNames = {
  'Ending Today': 'ending_today', // Placeholder, special case to handle differently
  'GovDeals': 'govdeals',
  'Wisconsin Surplus': 'wiscosurp',
  'HiBid': 'hibid',
  'Public Surplus': 'publicsurplus',
  'GSA': 'gsa',
  'Backes': 'backes',
  'Bidspotter': 'bidspotter',
  'SMC': 'smc',
  'Heartland': 'heartland',
  'Proxibid': 'proxibid'
};

// Configuration for icon appearance based on auction source
const iconConfigs = {
  govdeals: { text: 'GD', color: 'red' },
  wiscosurp: { text: 'WS', color: 'blue' },
  hibid: { text: 'HB', color: 'green' },
  publicsurplus: { text: 'PS', color: 'orange' },
  gsa: { text: 'GS', color: 'purple' },
  backes: { text: 'BK', color: 'cyan' },
  bidspotter: { text: 'BS', color: 'magenta' },
  smc: { text: 'SM', color: 'brown' },
  heartland: { text: 'HL', color: 'yellow' },
  proxibid: { text: 'PB', color: 'gray'},
  default: { text: '??', color: 'black' },
};

/**
 * Generates an SVG icon based on the category and size
 * @param {string} category - The category of the auction item
 * @param {number} size - The size of the cluster (if applicable)
 * @param {Array} featureCategories - Array of categories for features in a cluster
 * @returns {string} - Data URL of the generated SVG icon
 */
const generateSvgIcon = (category, size, featureCategories) => {
  let color;
  if (category === 'cluster' && Array.isArray(featureCategories)) {
    // Determine the most common color for cluster icons
    const colorCount = featureCategories.reduce((acc, cat) => {
      const categoryColor = iconConfigs[cat]?.color || 'gray';
      acc[categoryColor] = (acc[categoryColor] || 0) + 1;
      return acc;
    }, {});
    color = Object.entries(colorCount).sort((a, b) => b[1] - a[1])[0][0];
  } else {
    color = iconConfigs[category]?.color || iconConfigs.default.color;
  }
  const text = category === 'cluster' ? size : iconConfigs[category]?.text || iconConfigs.default.text;
  const svgString = `
    <svg xmlns="http://www.w3.org/2000/svg" width="50" height="50">
      <circle cx="25" cy="25" r="20" fill="${color}" />
      <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="white" font-size="16">${text}</text>
    </svg>
  `;
  return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgString);
};

/**
 * Determines the category of an item based on its URL
 * @param {string} url - The URL of the auction item
 * @returns {string} - The determined category or 'unknown' if not found
 */
const getCategoryFromUrl = (url) => {
  if (url && typeof url === 'string') {
    const category = Object.keys(iconConfigs).find(key => url.includes(key));
    if (category) return category;
  }
  return 'unknown';
};

/**
 * Groups an array of items by their category
 * @param {Array} items - Array of auction items
 * @returns {Object} - Object with categories as keys and arrays of items as values
 */
const groupItemsByCategory = (items) => {
  return items.reduce((acc, item) => {
    const category = item.category;
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(item);
    return acc;
  }, {});
};

// Export all functions and configurations
module.exports = {
  endpoints,
  tableNames,
  generateSvgIcon,
  getCategoryFromUrl,
  groupItemsByCategory
};