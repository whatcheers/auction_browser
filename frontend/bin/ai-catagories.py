import json

# Load the new JSON data from the provided file
file_path_new = 'ending_today.json'

with open(file_path_new, 'r') as file:
    auctions_new = json.load(file)

categories_new = {
    "Vehicles & Transport": [
        'ford', 'chevrolet', 'buick', 'dodge', 'harley', 'tractor', 'trailer', 'motorcycle', 'expedition', 'taurus', 'escape', 'silverado', 'pontiac', 'grand prix', 'f250', 'f350', 'ram', 'crown victoria', 'f450', 'escape hybrid', 'focus', 'truck', 'car', 'suv', 'van', 'pickup', 'bus', 'ambulance', 'atv', 'utv', 'snowmobile', 'boat', 'jet ski', 'camper', 'rv', 'motorhome', 'golf cart', 'forklift', 'lift', 'crane', 'excavator', 'dozer', 'loader', 'skid steer', 'backhoe', 'semi', 'dump truck', 'flatbed', 'tank', 'plow', 'spreader', 'mower', 'sweeper', 'sprayer', 'pump'
    ],
    "Computer & IT Equipment": [
        'apple', 'imac', 'macbook', 'airpod', 'laptop', 'desktop', 'computer', 'dell', 'keyboard', 'monitor', 'server', 'printer', 'scanner', 'projector', 'tablet', 'ipad', 'smartphone', 'iphone', 'android', 'router', 'modem', 'switch', 'firewall', 'nas', 'storage', 'hard drive', 'ssd', 'ram', 'cpu', 'gpu', 'motherboard', 'power supply', 'ups', 'surge protector', 'kvm', 'docking station', 'webcam', 'headset', 'microphone', 'speaker', 'software', 'license', 'antivirus', 'office', 'adobe', 'autocad'
    ],
    "Musical Equipment": [
        'drum', 'trombone', 'tuba', 'vibraphone', 'xylophone', 'marching band', 'music stands', 'sheet music', 'marching', 'band', 'musical', 'instrument', 'percussion', 'guitar', 'piano', 'keyboard', 'flute', 'clarinet', 'saxophone', 'trumpet', 'violin', 'cello', 'bass', 'amp', 'amplifier', 'microphone', 'speaker', 'mixer', 'equalizer', 'effects pedal', 'synthesizer', 'turntable', 'dj controller', 'headphones', 'in-ear monitor', 'metronome', 'tuner', 'case', 'stand', 'cable', 'string', 'pick', 'drumstick', 'capo', 'strap', 'music book', 'music software'
    ],
    "Office Furniture & Supplies": [
        'desk', 'chair', 'filing cabinet', 'office', 'supply', 'supplies', 'table', 'bookshelf', 'shelf', 'shredder', 'mail sorter', 'computer cart', 'cabinet', 'drawer', 'file folders', 'lateral file', 'organizer', 'bookcase', 'workspace', 'workstation', 'meeting table', 'conference', 'whiteboard', 'bulletin board', 'projector', 'monitor stand', 'keyboard tray', 'ergonomic', 'cubicle', 'partition', 'room divider', 'reception desk', 'waiting room', 'lobby', 'break room', 'cafeteria', 'lounge', 'executive', 'manager', 'task chair', 'stool', 'lectern', 'podium', 'easel', 'display', 'banner', 'sign', 'poster', 'frame', 'clock', 'coat rack', 'umbrella stand', 'trash can', 'recycling bin', 'paper', 'pen', 'pencil', 'marker', 'highlighter', 'stapler', 'tape', 'dispenser', 'scissors', 'ruler', 'calculator', 'binder', 'folder', 'envelope', 'label', 'post-it', 'notepad', 'calendar', 'planner', 'organizer', 'clipboard', 'business card', 'name tag', 'id badge', 'lanyard', 'key chain', 'flash drive', 'mouse pad', 'wrist rest', 'foot rest', 'lumbar support', 'air purifier', 'humidifier', 'dehumidifier', 'heater', 'fan', 'coffee maker', 'water cooler', 'refrigerator', 'microwave', 'toaster', 'blender', 'vending machine', 'first aid kit', 'fire extinguisher', 'smoke detector', 'carbon monoxide detector', 'security camera', 'access control', 'safe', 'cash box', 'time clock', 'employee handbook', 'training manual', 'reference book'
    ],
    "Outdoor & Gardening": [
        'mower', 'snow blower', 'golf', 'fishing', 'tackle box', 'landscaping', 'garden', 'hose', 'rake', 'shovel', 'trimmer', 'leaf blower', 'sprinkler', 'fertilizer spreader', 'seed spreader', 'wheelbarrow', 'outdoor', 'patio', 'grill', 'barbecue', 'lawn', 'pool', 'pond', 'fountain', 'deck', 'arbor', 'pergola', 'fire pit', 'outdoor lighting', 'landscape lighting', 'playground', 'swing set', 'trampoline', 'basketball hoop', 'soccer goal', 'volleyball net', 'tetherball', 'croquet', 'bocce', 'horseshoe', 'cornhole', 'picnic table', 'bench', 'chair', 'umbrella', 'gazebo', 'canopy', 'tent', 'hammock', 'bird feeder', 'bird bath', 'bird house', 'butterfly house', 'bat house', 'insect hotel', 'bee hive', 'composter', 'rain barrel', 'watering can', 'garden tool', 'pruner', 'lopper', 'trowel', 'cultivator', 'weeder', 'bulb planter', 'seeder', 'aerator', 'dethatcher', 'edger', 'sod cutter', 'lawn roller', 'lawn sweeper', 'leaf vacuum', 'chipper', 'shredder', 'log splitter', 'chainsaw', 'pole saw', 'hedge trimmer', 'brush cutter', 'pressure washer', 'generator', 'air compressor', 'welding machine', 'plasma cutter', 'metal detector', 'gold pan', 'sluice box', 'rock tumbler', 'telescope', 'microscope', 'binoculars', 'camera', 'trail camera', 'gps', 'compass', 'altimeter', 'barometer', 'thermometer', 'weather station', 'wind meter', 'rain gauge', 'snow gauge', 'soil tester', 'ph meter', 'moisture meter', 'light meter', 'fertilizer', 'pesticide', 'herbicide', 'fungicide', 'insecticide', 'animal repellent', 'deer fence', 'electric fence', 'barbed wire', 'chicken wire', 'livestock panel', 'gate', 'cattle guard', 'livestock waterer', 'stock tank', 'feed trough', 'hay feeder', 'salt lick', 'mineral block', 'saddle', 'bridle'
    ],
    "Cleaning Equipment": [
        'vacuum', 'mop', 'bucket', 'broom', 'dustpan', 'squeegee', 'pressure washer', 'floor scrubber', 'carpet cleaner', 'steam cleaner', 'window washer', 'disinfectant', 'sanitizer', 'bleach', 'detergent', 'rags', 'brush', 'cleaner', 'polisher', 'sweep', 'janitorial', 'cleaning cart', 'waste bin', 'trash can', 'recycling bin', 'vacuum cleaner', 'wet/dry vacuum', 'carpet extractor', 'floor buffer', 'burnisher', 'floor wax', 'floor stripper', 'floor sealer', 'dust mop', 'microfiber mop', 'sponge mop', 'toilet brush', 'toilet plunger', 'toilet cleaner', 'bathroom cleaner', 'glass cleaner', 'multi-surface cleaner', 'degreaser', 'disinfectant spray', 'air freshener', 'odor eliminator', 'cleaning cloths', 'cleaning wipes', 'cleaning gloves', 'cleaning apron', 'cleaning cart', 'cleaning caddy', 'cleaning sign', 'wet floor sign'
    ],
    "Industrial & Machinery": [
        'generator', 'compressor', 'welder', 'lathe', 'mill', 'drill press', 'saw', 'grinder', 'sander', 'pump', 'hydraulic', 'cnc', 'forklift', 'loader', 'excavator', 'bulldozer', 'tractor', 'crane', 'hoist', 'conveyor', 'pallet jack', 'workbench', 'vice', 'anvil', 'hammer drill', 'industrial fan', 'blower', 'mixer', 'batch plant', 'cutter', 'plasma cutter', 'water jet', 'laser', 'robot', 'automation', 'plc', 'motor', 'gearbox', 'bearing', 'coupling', 'sprocket', 'chain', 'belt', 'pulley', 'cylinder', 'valve', 'actuator', 'sensor', 'switch', 'gauge', 'meter', 'regulator', 'filter', 'separator', 'heat exchanger', 'boiler', 'furnace', 'oven', 'kiln', 'incinerator', 'refrigerator', 'freezer', 'chiller', 'air conditioner', 'dehumidifier', 'humidifier', 'air compressor', 'vacuum pump', 'blower', 'fan', 'dust collector', 'fume hood', 'clean room', 'laminar flow', 'hepa filter', 'cleanroom', 'esd', 'static control', 'ionizer', 'air shower', 'air lock', 'pass through', 'gowning room', 'locker', 'safety shower', 'eye wash', 'first aid', 'fire extinguisher', 'sprinkler', 'alarm', 'exit sign', 'emergency light', 'smoke detector', 'carbon monoxide detector', 'gas detector', 'radiation detector', 'geiger counter', 'dosimeter', 'hazmat', 'spill kit', 'containment', 'berm', 'absorbent', 'boom', 'skimmer', 'oil/water separator', 'clarifier', 'filtration', 'reverse osmosis', 'deionization', 'water treatment', 'wastewater treatment', 'sewage treatment', 'septic tank', 'leach field', 'sump pump', 'grease trap', 'oil interceptor', 'storm drain', 'catch basin', 'manhole', 'trench drain', 'floor drain', 'cleanout', 'backflow preventer', 'water meter', 'gas meter', 'electric meter', 'utility', 'pipeline', 'valve', 'fitting', 'flange', 'coupling', 'union', 'elbow', 'tee', 'reducer', 'expansion joint', 'strainer', 'gauge', 'pressure relief', 'safety valve', 'check valve', 'ball valve', 'gate valve', 'globe valve', 'butterfly valve', 'diaphragm valve', 'needle valve', 'plug valve', 'solenoid valve', 'actuator', 'positioner', 'transducer', 'transmitter', 'controller', 'recorder', 'indicator', 'alarm', 'switch', 'relay', 'circuit breaker', 'fuse', 'transformer', 'capacitor', 'reactor', 'inductor', 'resistor', 'thermocouple', 'rtd', 'thermistor', 'level switch', 'float switch', 'pressure switch', 'flow switch', 'limit switch', 'proximity switch', 'photo eye', 'motion sensor', 'smoke detector', 'heat detector', 'flame detector', 'gas detector', 'ph sensor', 'conductivity sensor', 'turbidity sensor', 'dissolved oxygen sensor', 'chlorine sensor', 'ammonia sensor', 'nitrate sensor', 'phosphate sensor', 'silica sensor', 'hardness sensor', 'color sensor', 'taste sensor', 'odor sensor', 'sound sensor', 'vibration sensor', 'accelerometer', 'strain gauge', 'load cell', 'torque sensor', 'speed sensor', 'tachometer', 'encoder', 'resolver', 'lvdt', 'rvdt', 'linear scale', 'rotary scale', 'glass scale', 'magnetic scale', 'laser interferometer', 'coordinate measuring machine', 'cmm', 'vision system', 'camera', 'barcode reader', 'rfid reader', 'label printer', 'marking machine', 'engraving machine', 'etching machine', 'cutting machine', 'welding machine', 'soldering machine', 'brazing machine', 'heat treating', 'annealing', 'normalizing', 'quenching', 'tempering', 'carburizing', 'nitriding', 'plating', 'coating', 'painting', 'powder coating', 'e-coating', 'anodizing', 'chrome plating', 'nickel plating', 'zinc plating', 'tin plating', 'silver plating', 'gold plating', 'copper plating', 'passivation', 'phosphating', 'blackening', 'bluing', 'parkerizing', 'galvanizing', 'sherardizing', 'terne plating', 'metal spraying', 'thermal spraying', 'plasma spraying', 'hvof', 'arc spraying', 'flame spraying', 'detonation gun', 'cold spray', 'electroless plating', 'electroforming', 'vacuum deposition', 'pvd', 'cvd', 'sputtering', 'evaporation', 'ion plating', 'ion implantation', 'diffusion', 'carburizing', 'nitriding', 'carbonitriding', 'ferritic nitrocarburizing', 'austenitic nitrocarburizing', 'boriding', 'titanium nitride', 'titanium carbonitride', 'titanium aluminum nitride', 'chromium nitride', 'zirconium nitride', 'diamond like carbon', 'dlc', 'silicon carbide', 'silicon nitride', 'aluminum oxide', 'zirconium oxide', 'yttria stabilized zirconia', 'magnesia stabilized zirconia', 'ceria stabilized zirconia', 'plasma electrolytic oxidation', 'micro arc oxidation', 'anodic spark deposition', 'keronite', 'tagnite', 'ceramax', 'cerakote', 'duracoat', 'gunkote', 'molycoat', 'xylan', 'teflon', 'halar', 'kynar', 'polyethylene', 'polypropylene', 'polyurethane', 'polyester'
    ],
    "Educational": [
        'textbook', 'book', 'notebook', 'educational', 'learning', 'teaching', 'classroom', 'school', 'blackboard', 'chalkboard', 'whiteboard', 'projector', 'laptop', 'tablet', 'educational software', 'microscope', 'calculator', 'globes', 'maps', 'charts', 'educational kit', 'science kit', 'math kit', 'art supplies', 'music stand', 'sheet music', 'instrument', 'lab equipment', 'educational toy', 'puzzle', 'educational game', 'flash cards', 'workbook', 'teacher edition', 'teacher guide', 'curriculum', 'lesson plan', 'assessment', 'test', 'quiz', 'exam', 'assignment', 'homework', 'project', 'presentation', 'report', 'essay', 'research paper', 'dissertation', 'thesis', 'journal', 'magazine', 'newspaper', 'encyclopedia', 'dictionary', 'thesaurus', 'almanac', 'atlas', 'biography', 'autobiography', 'memoir', 'novel', 'fiction', 'non-fiction', 'poetry', 'drama', 'screenplay', 'comic book', 'graphic novel', 'manga', 'coloring book', 'activity book', 'sticker book', 'pop-up book', 'board book', 'picture book', 'chapter book', 'young adult', 'children\'s literature', 'classic literature', 'world literature', 'ebook', 'audiobook', 'podcast', 'video lecture', 'online course', 'mooc', 'distance learning', 'homeschool', 'tutoring', 'study guide', 'reference book', 'textbook rental', 'library', 'bookstore', 'reading room', 'study room', 'computer lab', 'science lab', 'art studio', 'music room', 'gymnasium', 'auditorium', 'cafeteria', 'playground', 'field trip', 'school bus', 'locker', 'desk', 'chair', 'table', 'filing cabinet', 'bulletin board', 'display case', 'trophy case', 'flag', 'banner', 'pennant', 'yearbook', 'diploma', 'certificate', 'award', 'medal', 'ribbon', 'scholarship', 'grant', 'financial aid', 'student loan', 'tuition', 'fee', 'registration', 'enrollment', 'admission', 'orientation', 'graduation', 'commencement', 'alumni', 'reunion', 'homecoming', 'pep rally', 'spirit week', 'club', 'organization', 'student government', 'honor society', 'fraternity', 'sorority', 'sports team', 'mascot', 'cheerleader', 'marching band', 'orchestra', 'choir', 'drama club', 'debate', 'math team', 'science fair', 'spelling bee', 'geography bee', 'history day', 'model un', 'robotics competition', 'academic decathlon', 'quiz bowl', 'knowledge bowl', 'brain bowl', 'olympiad', 'tournament', 'championship', 'trophy', 'medal', 'award', 'prize', 'recognition', 'honor roll', 'dean\'s list', 'valedictorian', 'salutatorian', 'cum laude', 'magna cum laude', 'summa cum laude', 'phi beta kappa', 'national merit', 'ap scholar', 'international baccalaureate', 'montessori', 'waldorf', 'reggio emilia', 'experiential learning', 'project-based learning', 'inquiry-based learning', 'problem-based learning', 'cooperative learning', 'collaborative learning', 'flipped classroom', 'blended learning', 'personalized learning', 'adaptive learning', 'differentiated instruction', 'special education', 'gifted education', 'bilingual education', 'esl', 'ell', 'study abroad', 'exchange program', 'gap year', 'internship', 'co-op', 'apprenticeship', 'vocational training', 'career education', 'technical education', 'adult education', 'continuing education', 'lifelong learning', 'professional development', 'training', 'workshop', 'seminar', 'conference', 'symposium', 'forum', 'panel discussion', 'roundtable'
    ],
"Miscellaneous": []
}

# Function to determine the category of an item
def determine_category_new(item_name, categories):
    for category, keywords in categories.items():
        if any(keyword.lower() in item_name.lower() for keyword in keywords):
            return category
    return "Miscellaneous"

# Categorize each auction item
categorized_data_new = {category: [] for category in categories_new}
for auction in auctions_new:
    category = determine_category_new(auction["item_name"], categories_new)
    categorized_data_new[category].append(auction)

# Prepare HTML content with centered text and collapsible titles
html_content = """
<html>
<head>
<title>Categorized Auction Items</title>
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
<style>
body { font-family: 'Nunito', sans-serif; background-color: #f4f4f4; color: #333; text-align: center; margin: 0; padding: 20px; }
.collapsible { background-color: #007bff; color: white; cursor: pointer; padding: 10px; width: calc(100% - 20px); border: none; border-radius: 5px; text-align: center; outline: none; font-size: 16px; margin-bottom: 10px; transition: background-color 0.3s; }
.active, .collapsible:hover { background-color: #0056b3; }
.content { padding: 0 18px; display: none; overflow: hidden; background-color: white; text-align: left; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
.content ul { list-style-type: none; padding: 0; margin: 0; }
.content ul li { padding: 8px; border-bottom: 1px solid #ddd; }
.content ul li:last-child { border-bottom: none; }
.favorite { color: #ffc107; } /* Style for favorite items */
</style>
</head>
<body>
<h1>Categorized Auction Items</h1>
"""

# Dynamically add categorized items to the HTML content
for category, items in categorized_data_new.items():
    html_content += f'<button class="collapsible">{category} ({len(items)})</button>\n'
    html_content += '<div class="content">\n<ul>\n'
    for item in items:
        item_name = item["item_name"]
        item_url = item["url"]  # Use the 'url' field from your JSON data
        html_content += f'<li><a href="{item_url}" target="_blank">{item_name}</a></li>\n'
    html_content += '</ul>\n</div>\n'
    html_content += """
    <script>
    var coll = document.getElementsByClassName("collapsible");
    for (var i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function() {
            this.classList.toggle("active");
            var content = this.nextElementSibling;
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        });
    }
    </script>
    """

# Add closing HTML tags
html_content += """
</body>
</html>
"""

# Write the completed HTML content to a file with UTF-8 encoding
output_file_path = 'categorized_auction_items.html'
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    output_file.write(html_content)

print(f"Categorized items have been written to {output_file_path}")