from django.db import models


class ListingCategory(models.TextChoices):
    FOR_SALE = 'fs', 'For Sale'
    SERVICES = 'srv', 'Services'
    GIGS = 'gig', 'Gigs'
    JOBS = 'job', 'Jobs'

class ForSaleSubCategory(models.TextChoices):
    ANTIQUES = 'antiques'
    APPLIANCES = 'appliances'
    ARTS_CRAFTS = 'arts+crafts'
    ATV = 'atv+utv+sno'
    AUTO_PARTS = 'auto+parts'
    AVIATION = 'aviation'
    BABY_KID = 'baby+kid'
    BARTER = 'barter'
    BEAUTY_HLTH = 'beauty+hlth'
    BIKE_PARTS = 'bike+parts'
    BIKES = 'bikes'
    BOAT_PARTS = 'boat+parts'
    BOATS = 'boats'
    BOOKS = 'books'
    BUSINESS = 'business'
    CARS_TRUCKS = 'cars+trucks'
    CDS= 'cds+dvd+vhs'
    CELL_PHONES = 'cell+phones'
    CLOTHES_ACC = 'clothes+acc'
    COLLECTIBLES = 'collectibles'
    COMPUTER_PARTS = 'computer+parts'
    COMPUTERS = 'computers'
    ELECTRONICS = 'electronics'
    FARM_GARDEN = 'farm+garden'
    FREE = 'free'
    FURNITURE = 'furniture'
    GARAGE_SALE = 'garage+sale'
    GENERAL = 'general'
    HEAVY_EQUIP = 'heavy+equip'
    HOUSEHOLD = 'household'
    JEWELRY = 'jewelry'
    MATERIALS = 'materials'
    MOTORCYCLE_PARTS = 'moto+parts'
    MOTORCYCLES = 'motorcycles'
    MUSIC_INSTR = 'music+instr'
    PHOTO_VIDEO = 'photo+video'
    RVS_CAMP = 'rvs+camp'
    SPORTING = 'sporting'
    TICKETS = 'tickets'
    TOOLS = 'tools'
    TOYS_GAMES = 'toys+games'
    TRAILERS = 'trailers'
    VIDEO_GAMING = 'video+games'
    WANTED = 'wanted'
    WHEELS_TIRES = 'wheels+tires'

# class ServicesSubCategory(models.TextChoices):
#     AUTOMOTIVE = 'automotive'
#     BEAUTY = 'beauty'
#     cell/MOBILE = 'cell/mobile'
#     COMPUTER = 'computer'
#     CREATIVE = 'creative'
#     CYCLE = 'cycle'
#     EVENT = 'event'
#     farm+GARDEN = 'farm+garden'
#     FINANCIAL = 'financial'
#     health/WELL = 'health/well'
#     HOUSEHOLD = 'household'
#     labor/MOVE = 'labor/move'
#     LEGAL = 'legal'
#     LESSONS = 'lessons'
#     MARINE = 'marine'
#     PET = 'pet'
#     real ESTATE = 'real estate'
#     skilled TRADE = 'skilled trade'
#     sm biz ADS = 'sm biz ads'
#     travel/VAC = 'travel/vac'
#     write/ed/TRAN = 'write/ed/tran'

# class GigsSubCategory(models.TextChoices):
#     COMPUTER = 'computer'
#     CREATIVE = 'creative'
#     CREW = 'crew'
#     DOMESTIC = 'domestic'
#     EVENT = 'event'
#     LABOR = 'labor'
#     TALENT = 'talent'
#     WRITING = 'writing'

# class JobsSubCategory(models.TextChoices):
#     accounting+FINANCE = 'accounting+finance'
#     admin / OFFICE = 'admin / office'
#     arch / ENGINEERING = 'arch / engineering'
#     art / media / DESIGN = 'art / media / design'
#     biotech / SCIENCE = 'biotech / science'
#     business / MGMT = 'business / mgmt'
#     customer SERVICE = 'customer service'
#     EDUCATION = 'education'
#     etc / MISC = 'etc / misc'
#     food / bev / HOSP = 'food / bev / hosp'
#     general LABOR = 'general labor'
#     GOVERNMENT = 'government'
#     human RESOURCES = 'human resources'
#     legal / PARALEGAL = 'legal / paralegal'
#     MANUFACTURING = 'manufacturing'
#     marketing / pr / AD = 'marketing / pr / ad'
#     medical / HEALTH = 'medical / health'
#     nonprofit SECTOR = 'nonprofit sector'
#     real ESTATE = 'real estate'
#     retail / WHOLESALE = 'retail / wholesale'
#     sales / biz DEV = 'sales / biz dev'
#     salon / spa / FITNESS = 'salon / spa / fitness'
#     SECURITY = 'security'
#     skilled trade / CRAFT = 'skilled trade / craft'
#     software / qa / DBA = 'software / qa / dba'
#     systems / NETWORK = 'systems / network'
#     technical SUPPORT = 'technical support'
#     TRANSPORT = 'transport'
#     tv / film / VIDEO = 'tv / film / video'
#     web / info DESIGN = 'web / info design'
#     writing / EDITING = 'writing / editing'

# Model representing a marketplace listing
# fields to add later: images, contact info, user who posted, etc.
class Listing(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=128) 
    description = models.TextField()
    category = models.CharField(choices=ListingCategory.choices, default=ListingCategory.FOR_SALE)
    price = models.FloatField()
    subcategory = models.CharField(choices=ForSaleSubCategory.choices, default=ForSaleSubCategory.GENERAL)  # could be ForSaleSubCategory, ServicesSubCategory, etc.
    date_posted = models.DateTimeField(auto_now_add=True)
    # maybe get list of every city in FL?
    city = models.CharField(max_length=128) 
    # image = models.ImageField(upload_to='', default='default.jpg')
    email = models.EmailField(max_length=254, blank=True)
    phone = models.CharField(max_length=254, blank=True) 
    paid_for = models.BooleanField(default=False)  # want to add stripe payment processing before allowing the listing to be created

# want to update listing to use this model, to allow for multiple images
class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='listings/%Y/%m/%d/', default='default.jpg')
    

class Reply(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    sender = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='sent')
    recipient = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='received')
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    was_read_by_sender = models.BooleanField(default=False)
    was_read_by_recipient = models.BooleanField(default=False)
    # conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE, null=True, blank=True)

    def mark_read_by_user(self, user):
        if user == self.sender and not self.was_read_by_sender:
            self.was_read_by_sender = True
            self.save(update_fields=['was_read_by_sender'])  # Only updates this field in the DB
        elif user == self.recipient and not self.was_read_by_recipient:
            self.was_read_by_recipient = True
            self.save(update_fields=['was_read_by_recipient'])  # Only updates this field in the DB

# class Conversation(models.Model):
#     listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
#     user1 = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='conversation_user1')
#     user2 = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='conversation_user2')
#     last_updated = models.DateTimeField(auto_now=True)

FL_CITIES = [
    "Alachua",
    "Altamonte Springs",
    "Anna Maria",
    "Apalachicola",
    "Apopka",
    "Arcadia",
    "Archer",
    "Astalula",
    "Atlantic Beach",
    "Atlantis",
    "Auburndale",
    "Aventura",
    "Avon Park",
    "Bal Harbour",
    "Baldwin",
    "Bartow",
    "Bay Harbor Islands",
    "Bay Lake",
    "Bell",
    "Belle Glade",
    "Belle Isle",
    "Belleair",
    "Belleair Beach",
    "Belleair Bluffs",
    "Belleair Shore",
    "Belleview",
    "Beverley Beach",
    "Biscayne Park",
    "Blountstown",
    "Boca Raton",
    "Boynton Beach",
    "Bradenton",
    "Bradenton Beach",
    "Branford",
    "Bristol",
    "Bronson",
    "Brooker",
    "Brooksville",
    "Bunnell",
    "Bushnell",
    "Callahan",
    "Callaway",
    "Cape Canaveral",
    "Cape Coral",
    "Casselberry",
    "Cedar Key",
    "Center Hill",
    "Century",
    "Chattahoochee",
    "Chiefland",
    "Chipley",
    "Cinco Bayou",
    "Clearwater",
    "Clermont",
    "Clewiston",
    "Cocoa ",
    "Cocoa Beach",
    "Coconut Creek",
    "Coleman",
    "Cooper City",
    "Coral Gables",
    "Coral Springs",
    "Cottondale",
    "Crescent City",
    "Crestview",
    "Cross City",
    "Crystal River",
    "Cutler Bay",
    "Dade City",
    "Dania Beach",
    "Davenport",
    "Davie",
    "Daytona Beach",
    "Daytona Beach Shores",
    "De Bary",
    "DeFuniak Springs",
    "Deerfield Beach",
    "Deland",
    "Delray Beach",
    "Deltona",
    "Destin",
    "Doral",
    "Dunedin",
    "Dunnellon",
    "Edgewater",
    "Edgewood",
    "El Portal",
    "Estero",
    "Esto",
    "Eustis",
    "Everglades City",
    "Fanning Springs",
    "Fellsmere",
    "Fernandina Beach",
    "Flagler Beach",
    "Florida City",
    "Fort Lauderdale",
    "Fort Meade",
    "Fort Myers",
    "Fort Myers Beach",
    "Fort Pierce",
    "Fort Walton Beach",
    "Fort White",
    "Freeport",
    "Frostproof",
    "Fruitland Park",
    "Gainesville",
    "Glen Saint Mary",
    "Golden Beach",
    "Golf",
    "Grant-Valkaria",
    "Green Cove Springs",
    "Greenacres",
    "Greensboro",
    "Greenville",
    "Gretna",
    "Groveland",
    "Gulf Breeze",
    "Gulfport",
    "Haines City",
    "Hallandale Beach",
    "Hampton",
    "Havana",
    "Haverhill",
    "Hawthorne",
    "Hialeah",
    "Hialeah Gardens",
    "High Springs",
    "Highland Beach",
    "Highland Park",
    "Hilliard",
    "Hillsboro Beach",
    "Holly Hill",
    "Hollywood",
    "Holmes Beach",
    "Homestead",
    "Howey-in-the-Hills",
    "Hypoluxo",
    "Indialantic",
    "Indian Creek",
    "Indian Harbour Beach",
    "Indian River Shores",
    "Indian Shores",
    "Indiantown",
    "Inglis",
    "Interlachen",
    "Inverness",
    "Islamorada, Village of Islands",
    "Jacksonville",
    "Jacksonville Beach",
    "Jasper",
    "Jay",
    "Juno Beach",
    "Jupiter",
    "Jupiter Inlet Colony",
    "Jupiter Island",
    "Kenneth City",
    "Key Biscayne",
    "Key Colony Beach",
    "Key West",
    "Keystone Heights",
    "Kissimmee",
    "La Crosse",
    "LaBelle",
    "Lady Lake",
    "Lake Alfred",
    "Lake Buena Vista",
    "Lake Butler",
    "Lake City",
    "Lake Clark Shores",
    "Lake Hamilton",
    "Lake Helen",
    "Lake Mary",
    "Lake Park",
    "Lake Placid",
    "Lake Wales",
    "Lake Worth Beach",
    "Lakeland",
    "Lantana",
    "Largo",
    "Lauderdale Lakes",
    "Lauderdale-By-The-Sea",
    "Lauderhill",
    "Layton",
    "Lazy Lake",
    "Lee",
    "Leesburg",
    "Lighthouse Point",
    "Live Oak",
    "Longboat Key",
    "Longwood",
    "Loxahatchee Groves",
    "Lynn Haven",
    "Macclenny",
    "Madeira Beach",
    "Madison",
    "Maitland",
    "Malabar",
    "Manalapan",
    "Mangonia Park",
    "Marathon",
    "Marco Island",
    "Margate",
    "Marianna",
    "Mary Esther",
    "Mascotte",
    "McIntosh",
    "Medley",
    "Melbourne",
    "Melbourne Beach",
    "Melbourne Village",
    "Mexico Beach",
    "Miami",
    "Miami Beach",
    "Miami Gardens",
    "Miami Lakes",
    "Miami Shores",
    "Miami Springs",
    "Micanopy",
    "Midway",
    "Milton",
    "Minneola",
    "Miramar",
    "Monticello",
    "Montverde",
    "Moore Haven",
    "Mount Dora",
    "Mulberry",
    "Naples",
    "Neptune Beach",
    "New Port Richey",
    "New Smyrna Beach",
    "Newberry",
    "Niceville",
    "North Bay Village",
    "North Lauderdale",
    "North Miami",
    "North Miami Beach",
    "North Palm Beach",
    "North Port",
    "North Redington Beach",
    "Oak Hill",
    "Oakland",
    "Oakland Park",
    "Ocala",
    "Ocean Breeze",
    "Ocean Ridge",
    "Ocoee",
    "Okeechobee",
    "Oldsmar",
    "Opa-locka",
    "Orange City",
    "Orange Park",
    "Orchid",
    "Orlando",
    "Ormond Beach",
    "Oviedo",
    "Pahokee",
    "Palatka",
    "Palm Bay",
    "Palm Beach",
    "Palm Beach Gardens",
    "Palm Beach Shores",
    "Palm Coast",
    "Palm Shores",
    "Palm Springs",
    "Palmetto",
    "Palmetto Bay",
    "Panama City",
    "Panama City Beach",
    "Parker",
    "Parkland",
    "Paxton",
    "Pembroke Park",
    "Pembroke Pines",
    "Penney Farms",
    "Pensacola",
    "Perry",
    "Pierson",
    "Pinecrest",
    "Pinellas Park",
    "Plant City",
    "Plantation",
    "Polk City",
    "Pomona Park",
    "Pompano Beach",
    "Ponce Inlet",
    "Port Orange",
    "Port Richey",
    "Port St. Joe",
    "Port St. Lucie",
    "Punta Gorda",
    "Quincy",
    "Reddick",
    "Redington Beach",
    "Redington Shores",
    "Riviera Beach",
    "Rockledge ",
    "Royal Palm Beach",
    "Safety Harbor",
    "San Antonio",
    "Sanford",
    "Sanibel",
    "Sarasota",
    "Satellite Beach",
    "Sebastian",
    "Sebring",
    "Sewall's Point",
    "Shalimar",
    "Sneads",
    "Sopchoppy",
    "South Bay",
    "South Daytona",
    "South Miami",
    "South Palm Beach",
    "South Pasadena",
    "Southwest Ranches",
    "Springfield",
    "St. Augustine",
    "St. Augustine Beach",
    "St. Cloud",
    "St. Leo",
    "St. Lucie Village",
    "St. Marks",
    "St. Pete Beach",
    "St. Petersburg",
    "Starke",
    "Stuart",
    "Sunny Isles Beach",
    "Sunrise",
    "Surfside",
    "Sweetwater",
    "Tallahassee",
    "Tamarac",
    "Tampa",
    "Tarpon Springs",
    "Tavares",
    "Temple Terrace",
    "Tequesta",
    "Titusville",
    "Treasure Island",
    "Trenton",
    "Umatilla",
    "Valparaiso",
    "Venice",
    "Vero Beach",
    "Virginia Gardens",
    "Waldo",
    "Wachula",
    "Webster",
    "Welaka",
    "Wellington",
    "West Melbourne",
    "West Miami",
    "West Palm Beach",
    "West Park",
    "Westlake",
    "Weston",
    "Wewahitchka",
    "White Springs",
    "Wildwood",
    "Wilton Manors",
    "Windermere",
    "Winter Garden",
    "Winter Haven",
    "Winter Park",
    "Winter Springs",
    "Yankeetown",
    "Zephyrhills",
    "Zolfo Springs"
]
