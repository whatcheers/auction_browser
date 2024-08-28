const categories = {
  'Fleet Maintenance and Vehicles': [
    'acura', 'air filter', 'alfa romeo', 'alignment', 'aston martin', 'atv', 'audi', 'backhoe', 'battery', 'bentley',
    'bmw', 'bobcat', 'boom lift', 'brakes', 'bugatti', 'bus', 'byd', 'car', 'case', 'caterpillar', 'cherry picker',
    'chevrolet', 'chrysler', 'citroën', 'clutch', 'coolant system', 'coupe', 'crane', 'daf', 'daewoo', 'ditch witch',
    'dodge', 'ducati', 'dump truck', 'electric vehicle', 'emergency vehicle', 'engine', 'excavator', 'exhaust',
    'ferrari', 'fiat', 'fire truck', 'ford', 'forklift', 'freightliner', 'fuel filter', 'fuso', 'garbage truck',
    'genesis', 'geely', 'gmc', 'golf cart', 'great wall', 'harley', 'headlights', 'hino', 'hitachi', 'honda',
    'hybrid', 'hyundai', 'infiniti', 'international', 'isuzu', 'iveco', 'jaguar', 'jeep', 'john deere', 'kawasaki',
    'kenworth', 'komatsu', 'kubota', 'lamborghini', 'land rover', 'lexus', 'loader', 'lotus', 'mack', 'mahindra',
    'manlift', 'maserati', 'mazda', 'mclaren', 'mercedes', 'mini', 'mitsubishi', 'muffler', 'nikola', 'nissan',
    'oil change', 'pallet jack', 'paver', 'peugeot', 'peterbilt', 'plow', 'police car', 'polaris', 'porsche',
    'proton', 'radiators', 'ram', 'renault', 'rivian', 'roadway signs', 'roller', 'rolls-royce', 'saic', 'scania',
    'scissor lift', 'seat', 'sedan', 'shock absorbers', 'skid steer', 'skoda', 'smart', 'snow plow', 'snowmobile',
    'spark plug', 'ssangyong', 'street sweeper', 'subaru', 'suspension', 'suzuki', 'tata', 'taillights', 'tata',
    'terex', 'tesla', 'timing belt', 'tire', 'tow truck', 'tractor', 'trailer', 'transmission', 'truck', 'utv',
    'van', 'volkswagen', 'volvo', 'windshield', 'yamaha', 'zhongtong', 'pumper', "Seadoo", "Argo", "Toro", "Vehicle Wash",
     'motorcycle', 'scooter', 'explorer', 'ford', 'chevrolet', 'dodge', 'freightliner'
  ],

  'Industrial and Commercial Equipment': [
    'air compressor', 'alto sham', 'amplifier', 'audio equipment', 'bagel slicer', 'bending', 'boiler', 'boring', 'bottling',
    'bun slicer', 'butcher block', 'canning', 'casting', 'chiller', 'cnc', 'coating', 'commercial oven', 'conveyor',
    'conveying', 'cutting', 'drill press', 'drilling', 'excavator', 'exercise equipment', 'fabrication', 'filling',
    'floor mixer', 'forging', 'griddle oven', 'grinding', 'heat treating', 'heavy machinery', 'hobart mixer', 'hobart slicer',
    'hvac', 'industrial mixer', 'injection molding', 'labeling', 'laboratory equipment', 'laminating', 'lathe', 'machining',
    'material handling', 'medical equipment', 'metalworking', 'milling', 'moline slicer', 'mortar mixer', 'panini press',
    'painting', 'peltier', 'pioneer', 'pitching machine', 'plasma cutter', 'plastics', 'plating', 'playground set', 'punching',
    'refrigeration', 'rolling', 'sandblaster', 'scba', 'sealing', 'shearing', 'sony', 'soup server', 'spectrometer',
    'spectrophotometer', 'spectrophotonmeter', 'stamping', 'studio light', 'therapy tub', 'tractor', 'ventilation fan',
    'warming', 'welding', 'welder', 'water hand pump', 'water pump', 'woodworking', 'yamaha', 'MSA', 'chains', "Sharpener", 
    "Tree Spade", "Detector Check Valve", "Fire Flow Strainer", "Floor Sweeper", "Hoist Motor", "Wood Chipper", "Pipe Bender", 
    "Pipe Cutter", "Tonometer", "Photometer", "Buffalo Chopper", "Plate Compactor", "Dust Collection System", "Paint Machine", 
    "PTO Generator", "Steam Kettle", "Screw Food Extruder", "Vending Machine", "AccuTemp", "Beuthling", "Math Literacy", 
    "Chemistry", 'kiln', 'vacuum', 'industrial', 'commercial', 'pressure washer', 'generator'
  ],

  'Office Equipment and Furniture': [
    'adjustable', 'amplifier', 'apc', 'APC', 'APC batteries', 'apple', 'armoire', 'audio', 'auditorium', 'boardroom',
    'bose', 'bookshelf', 'binding', 'break room', 'bose', 'boardroom', 'cables', 'cafeteria', 'cabinet', 'cables',
    'chair', 'classroom', 'computer', 'conference', 'copier', 'credenza', 'crestron', 'cubby', 'cubicle', 'desk',
    'dell', 'desktop', 'display', 'divider', 'dvd player', 'drafting table', 'ergonomic', 'extron', 'executive',
    'fax', 'file cabinet', 'file cabinets', 'filing', 'filing cabinet', 'folder', 'folding', 'fsr', 'fueling system',
    'furniture', 'guest', 'hutch', 'imac', 'ipad', 'ipads', 'jvc', 'keyboard', 'laminating', 'laptop', 'lecture hall',
    'lectrosonics', 'library', 'locker', 'meeting', 'modular', 'monitor', 'mouse', 'nesting', 'office furniture',
    'office supplies', 'panasonic', 'partition', 'phone', 'power adapters', 'presentation', 'printer', 'projector',
    'prop meter', 'qsc', 'reception', 'safe', 'scanner', 'screen', 'server', 'shelving', 'shredder', 'sit-stand',
    'stacking', 'standing desk', 'storage', 'storage cabinet', 'task', 'Toughbooks', 'training', 'tvone', 'under desk cabinets',
    'vhs', 'video', 'video monitor', 'waiting room', 'whiteboard', 'workstation', 'modems', "Easels", "Office Table", "Side Tables", 
    "Network Switch", "Binder Machine", "Washer and Dryer", "Commercial Refrigerator", "Glass Door Merchandiser", 
    "Equipment Lift Table", 'desk', 'file cabinet', 'lateral file', 'chair', 'table', 'drafting table', 'standing desk'
  ],

  'MRO (Maintenance, Repair, and Operations)': [
    'accessory', 'adhesive', 'air tool', 'allen-bradley', 'belt', 'breaker', 'broom', 'buffer', 'bucket', 'cart',
    'caulk', 'clamp', 'cleaning', 'cordless tool', 'degreaser', 'dolly', 'drill', 'dustpan', 'electrical', 'extension cord',
    'fan', 'fire extinguisher', 'first aid', 'flagging tape', 'flashlight', 'fuse', 'garbage cans', 'grease', 'grinder',
    'grout', 'hammer', 'hand truck', 'hardware', 'hilti', 'hvac', 'impact', 'janitorial', 'ladder', 'level', 'lubricant',
    'mop', 'mortar', 'mounting brackets', 'oil', 'paint sprayer', 'pallet', 'patch', 'pitchfork', 'pliers', 'polisher',
    'power conditioner', 'power supply', 'power tool', 'rake', 'ratchet', 'reel', 'relay', 'repair kit', 'rust remover',
    'safety equipment', 'sander', 'scaffolding', 'schneider', 'schneider', 'screwdriver', 'sealant', 'sequencer', 'shelf',
    'shelving', 'siemens', 'soldering', 'socket', 'spare part', 'storage', 'saw', 'scale', 'smith blair', 'tape measure',
    'tile', 'tilt', 'tool', 'torque', 'trash can', 'vacuum', 'vaccuum', 'vise', 'welding', 'wheelbarrow', 'wrench',
    'wrench set', 'workbench', 'pressure washer', "Router Bits", "Dremel", "Reamers", "Tappers", "Surveyor Stand", 
    "Compression Kit", "Weights", "Regulator Valves", "Vac Sealer", "Painter Supplies", "Solder Gun", "Electric Range", 
    "Porta Power", "Steel Toes", "Air Brush", "Trimmers", "Insulation Tester", 'cable', 'tool', 'hardware', 'supplies', 'hand truck', 'bucket'
  ],

  'Retail and Consumer Goods': [
    'action camera', 'action figure', 'amplifier', 'augmented reality', 'bass', 'bike', 'bikes', 'board game', 'boombox',
    'book', 'camcorder', 'cash', 'cashier', 'collectible', 'color video monitor', 'consumer electronic', 'cooler',
    'cookware', 'digital camera', 'discman', 'dishes', 'doll', 'drone', 'drum', 'e-reader', 'effects pedal', 'fitness tracker',
    'futon', 'game console', 'gaming chair', 'gaming desk', 'gaming headset', 'gaming keyboard', 'gaming laptop', 'gaming mouse',
    'gaming pc', 'gps', 'guitar', 'gym mats', 'headphones', 'home appliance', 'home theater', 'ipod', 'keyboard', 'lego',
    'media', 'memorabilia', 'microphone', 'model kit', 'motivational pictures', 'mp3 player', 'nintendo', 'outdoor gear',
    'playstation', 'plush', 'projector', 'puzzle', 'radio', 'rc boat', 'rc car', 'rc plane', 'record player', 'screen',
    'smartphone', 'smartwatch', 'soundbar', 'speakers', 'sports equipment', 'stereo', 'studio', 'surround sound', 'synthesizer',
    'tablet', 'television', 'trading card', 'turntable', 'virtual reality', 'walkman', 'xbox', 'slide', "Tables", "Nike", 
    "Baseball Cleats", "Football Jersey", "Game Jersey", "Pharmacology", 'TV', 'tv', 'television',  'consumer', 'retail'
  ],
  'Real Estate': [
    'acre', 'agricultural', 'airbnb', 'apartment', 'bed and breakfast', 'boat slip', 'campground', 'carport', 'city lots',
    'co-op', 'commercial lot', 'commercial property', 'community', 'condominium', 'covenant', 'dock', 'duplex',
    'easement', 'encumbrance', 'farm', 'foreclosure', 'fourplex', 'full service lease', 'garage', 'gross lease',
    'ground lease', 'hotel', 'industrial land', 'land', 'leasehold', 'lien', 'Lot', 'manufactured home', 'marina',
    'master lease', 'mineral rights', 'mining', 'mobile home', 'modular home', 'motel', 'multi family', 'net lease',
    'office building', 'orchard', 'parking', 'parking', 'parking', 'parking', 'percentage lease', 'probate', 'ranch',
    'reo', 'residential lot', 'resort', 'restriction', 'retail space', 'right of way', 'rv park', 'short sale',
    'short-term rental', 'single family', 'sq ft', 'storage facility', 'sublease', 'timber', 'timeshare', 'tiny home',
    'townhouse', 'triplex', 'vacation rental', 'vineyard', 'vrbo', 'warehouse', 'water rights', 'Discounted Property'
  ],
  'Clothing': [
    'Jerseys', 'shirt', 'pants', 'jacket','Nike', 'Baseball Cleats', 'Football Jersey', 'Game Jersey'
  ],
  'Electronics and Technology': [
    'computer', 'monitor', 'printer', 'projector', 'laptop', 'desktop', 'server', 'ups', 'battery backup',
    'scanner', 'copier', 'keyboard', 'mouse', 'cable', 'network', 'switch', 'router'
  ],
  'Auction Information': [
    'viewing', 'pickup', 'auction'
  ]
};

const categorizeItems = (itemData) => {
  return itemData.map(item => {
    const lowercaseItemName = item.item_name.toLowerCase();
    
    for (const [category, keywords] of Object.entries(categories)) {
      if (keywords.some(keyword => lowercaseItemName.includes(keyword.toLowerCase()))) {
        return { ...item, category };
      }
    }
 
    // Additional checks for specific patterns
    if (/\d{4}.*(?:ford|chevrolet|dodge|freightliner)/i.test(lowercaseItemName)) {
      return { ...item, category: 'Fleet Maintenance and Vehicles' };
    }
    
    if (/(?:metal|wood(?:en)?)\s+(?:desk|table|cabinet)/i.test(lowercaseItemName)) {
      return { ...item, category: 'Office Equipment and Furniture' };
    }
    
    return { ...item, category: 'Uncategorized' };
  });
};

module.exports = { categorizeItems, categories };