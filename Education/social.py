from shutil import which
import re

tamil_nadu = {
    1: "how many districts in tamil nadu: Tamil Nadu has 38 districts.",
    2: "who is the chief minister of tamil nadu: The Chief Minister is M. K. Stalin (2025).",
    3: "who is the governor of tamil nadu: The Governor is R. N. Ravi (2025).",
    4: "what is the capital of tamil nadu: Chennai.",
    5: "how many people live in tamil nadu: Around 82 million (2025 estimate).",
    6: "what is the language of tamil nadu: Tamil.",
    7: "what is the area of tamil nadu: 130,058 square kilometres.",
    8: "what is the literacy rate of tamil nadu: About 80%.",
    9: "what is the sex ratio of tamil nadu: Around 996 females per 1000 males.",
    10: "which rivers flow in tamil nadu: Cauvery, Vaigai, Thamirabarani, Palar.",
    11: "who are famous leaders of tamil nadu: Periyar, K. Kamaraj, C. N. Annadurai, M. G. Ramachandran, J. Jayalalithaa.",
    12: "what is the history of tamil nadu: Ruled by Cholas, Pandyas, Cheras, Pallavas, Vijayanagara, Nayaks, British; became Tamil Nadu in 1969.",
    13: "what is the culture of tamil nadu: Bharatanatyam, Carnatic music, Pongal, temples, Tamil literature.",
    14: "what are tourist places in tamil nadu: Chennai, Madurai, Thanjavur, Rameswaram, Ooty, Kodaikanal, Mahabalipuram.",
    15: "what is the economy of tamil nadu: IT, automobile, textiles, agriculture, films, tourism.",
    16: "what are major industries in tamil nadu: Automobile, textiles, leather, IT, agriculture, film industry.",
    17: "what is the main occupation in tamil nadu: Agriculture and industrial/service jobs.",
    18: "what is the climate of tamil nadu: Tropical climate with hot summers, moderate winters, monsoons.",
    19: "which are the major ports of tamil nadu: Chennai, Ennore, Tuticorin, Karaikal.",
    20: "what are important festivals in tamil nadu: Pongal, Tamil New Year, Deepavali, Karthigai Deepam, Chithirai Festival.",
    21: "what are major crops in tamil nadu: Rice, sugarcane, bananas, coconut, millets, cotton.",
    22: "which mountains are in tamil nadu: Western Ghats and Eastern Ghats.",
    23: "which wildlife sanctuaries are in tamil nadu: Mudumalai, Vedanthangal, Guindy National Park, Kalakkad Mundanthurai.",
    24: "what is the transport system in tamil nadu: Road, rail, air; metro in Chennai; state buses and private transport.",
    25: "how many airports are in tamil nadu: Chennai, Coimbatore, Madurai, Tiruchirapalli, Salem.",
    26: "what is the main religion in tamil nadu: Hinduism, followed by Islam and Christianity.",
    27: "what are important temples in tamil nadu: Meenakshi Temple, Brihadeeswarar Temple, Rameswaram, Kanchipuram Temples.",
    28: "who is the first CM of tamil nadu: C. N. Annadurai.",
    29: "what is the official emblem of tamil nadu: Srivilliputhur Temple tower.",
    30: "what is the state animal of tamil nadu: Nilgiri tahr.",
    31: "what is the state bird of tamil nadu: Emerald dove.",
    32: "what is the state flower of tamil nadu: Gloriosa lily.",
    33: "what is the state tree of tamil nadu: Palm tree.",
    34: "which is the highest peak in tamil nadu: Anamudi Peak (border with Kerala).",
    35: "which is the longest river in tamil nadu: Cauvery River.",
    36: "which is the largest city in tamil nadu: Chennai.",
    37: "which districts are in northern tamil nadu: Chennai, Vellore, Tiruvallur, Krishnagiri, etc.",
    38: "which districts are in southern tamil nadu: Madurai, Thoothukudi, Tirunelveli, Kanyakumari, etc.",
    39: "what is the human development index in tamil nadu: One of the higher HDI among Indian states.",
    40: "which are famous educational institutions in tamil nadu: IIT Madras, Anna University, Madras Medical College, University of Madras.",
    41: "what is the major port city in tamil nadu: Chennai.",
    42: "who are famous freedom fighters from tamil nadu: V. O. Chidambaram Pillai, Subramanya Bharathi, C. Rajagopalachari.",
    43: "what is the traditional dress in tamil nadu: Saree for women, dhoti and shirt for men.",
    44: "which is the most visited hill station in tamil nadu: Ooty and Kodaikanal.",
    45: "what is the main cuisine in tamil nadu: Rice-based meals, sambar, rasam, idli, dosa, Pongal.",
    46: "which industries are in Coimbatore: Textiles, engineering, IT.",
    47: "which industries are in Chennai: Automobile manufacturing, IT, electronics, shipping.",
    48: "who are famous poets from tamil nadu: Thiruvalluvar, Subramanya Bharathi, Bharathidasan.",
    49: "what is the main sport in tamil nadu: Kabaddi and cricket.",
    50: "which is the famous dance of tamil nadu: Bharatanatyam.",
    52: "which is the major festival celebrated in villages: Pongal.",
    53: "which is the major festival celebrated in cities: Tamil New Year and Deepavali.",
    54: "which are famous temples in Kanchipuram: Kailasanathar, Ekambareswarar, Varadaraja Perumal.",
    55: "which are famous temples in Madurai: Meenakshi Amman Temple, Thirumalai Nayakar Mahal.",
    56: "which are famous temples in Thanjavur: Brihadeeswarar Temple, Thanjavur Maratha Palace.",
    57: "which are famous temples in Rameswaram: Ramanathaswamy Temple.",
    58: "which are famous hill stations in tamil nadu: Ooty, Kodaikanal, Yercaud, Valparai.",
    59: "which is the main port in tamil nadu: Chennai Port.",
    60: "which is the second major port in tamil nadu: Tuticorin Port (V.O. Chidambaranar Port).",
    61: "which is the main IT hub in tamil nadu: Chennai and Coimbatore.",
    62: "which districts are famous for textiles: Coimbatore, Salem, Tirupur.",
    63: "which district is famous for temples: Madurai.",
    64: "which district is famous for hill stations: Nilgiris, Kodaikanal, Dindigul.",
    65: "which districts are in western tamil nadu: Coimbatore, Erode, Nilgiris.",
    66: "which districts are in eastern tamil nadu: Chennai, Cuddalore, Villupuram.",
    67: "which districts are in central tamil nadu: Tiruchirapalli, Thanjavur, Karur.",
    68: "which districts are in southern tamil nadu: Madurai, Thoothukudi, Tirunelveli, Kanyakumari.",
    69: "which rivers are famous for irrigation: Cauvery, Vaigai.",
    70: "which districts are coastal: Chennai, Thoothukudi, Nagapattinam, Ramanathapuram.",
    71: "which districts have special economic zones: Chennai, Coimbatore, Tirunelveli.",
    72: "which industries are in Thoothukudi: Port-based industries, shipping, chemical industries.",
    73: "which industries are in Salem: Textiles, steel, cement.",
    74: "which industries are in Tiruchirapalli: Heavy engineering, ceramics, education hubs.",
    75: "which is the most industrialized district: Chennai.",
    76: "which is the largest district by area: Villupuram.",
    77: "which is the smallest district by area: Chennai.",
    78: "which districts are famous for agriculture: Thanjavur, Tiruvannamalai, Thiruvarur.",
    79: "which districts are famous for silk: Kanchipuram, Salem.",
    80: "which districts are famous for handicrafts: Kanchipuram, Madurai, Thanjavur.",
    81: "which district is famous for pearls: Thoothukudi.",
    82: "which district is famous for wind energy: Coimbatore, Tirunelveli, Tuticorin.",
    83: "which districts are famous for tourism: Nilgiris, Kodaikanal, Madurai, Mahabalipuram.",
    84: "which district has UNESCO World Heritage Sites: Thanjavur (Brihadeeswarar Temple), Mahabalipuram.",
    85: "which districts have major educational hubs: Chennai, Coimbatore, Madurai.",
    86: "which district is famous for medical institutions: Chennai.",
    87: "which districts are famous for silk weaving: Kanchipuram, Salem.",
    88: "which districts are famous for traditional arts: Madurai, Thanjavur.",
    89: "which districts are famous for Carnatic music festivals: Chennai, Thanjavur.",
    90: "which district hosts the famous Pongal celebrations: Thanjavur, Madurai, Villupuram.",
    91: "which districts are famous for temples and architecture: Kanchipuram, Madurai, Thanjavur.",
    92: "which districts are famous for hill stations and tourism: Nilgiris, Dindigul, Kodaikanal.",
    93: "which districts are famous for textile industries: Coimbatore, Tirupur, Salem.",
    94: "which districts are famous for IT companies: Chennai, Coimbatore, Madurai.",
    95: "which districts are famous for automobile industries: Chennai, Hosur, Sriperumbudur.",
    96: "which districts are famous for agriculture: Thanjavur, Tiruvallur, Thiruvarur.",
    97: "which districts are famous for coconut production: Thoothukudi, Kanyakumari, Nagapattinam.",
    98: "which districts are famous for banana cultivation: Theni, Tiruchirapalli, Erode.",
    99: "which districts are famous for sugarcane: Thanjavur, Vellore, Tiruvannamalai.",
    100: "which districts are famous for tourism and heritage: Madurai, Thanjavur, Kanchipuram, Mahabalipuram."
}

def _find_info(query: str, data_dict: dict):
    if not query:
        return "Sorry, I didn't catch your question."
    q = query.lower().strip()
    
    stop_words = {"what", "is", "the", "of", "in", "are", "which", "who", "how", "many", "tell", "me", "about", "can", "you", "please"}
    query_words = set(re.findall(r'\b\w+\b', q)) - stop_words

    best_match = None
    max_overlap = 0

    for value in data_dict.values():
        val_lower = value.lower()
        if ":" in val_lower:
            q_part, a_part = val_lower.split(":", 1)
        else:
            q_part, a_part = val_lower, val_lower

        # Direct inclusion
        if q in val_lower or q_part.strip() in q:
            return value

        # Overlap ranking
        q_words = set(re.findall(r'\b\w+\b', q_part)) - stop_words
        overlap = len(query_words & q_words)
        if overlap > max_overlap and overlap >= 2:
            max_overlap = overlap
            best_match = value

    if best_match:
        return best_match
    return "Sorry, I don't know the answer."


def tamil_nadu_info(query: str):
    return _find_info(query, tamil_nadu)

andhra_pradesh = {
    1: "how many districts in andhra pradesh: Andhra Pradesh has 26 districts.",
    2: "who is the chief minister of andhra pradesh: The Chief Minister (2025) is Y. S. Jagan Mohan Reddy.",
    3: "who is the governor of andhra pradesh: The Governor (2025) is S. Abdul Nazeer.",
    4: "what is the capital of andhra pradesh: Amaravati (legislative), Visakhapatnam (executive & planning).",
    5: "how many people live in andhra pradesh: Around 53 million (2025 estimate).",
    6: "what is the language of andhra pradesh: Telugu is the official language.",
    7: "what is the area of andhra pradesh: 162,970 square kilometres.",
    8: "what is the literacy rate of andhra pradesh: About 67.41%.",
    9: "what is the sex ratio of andhra pradesh: Around 992 females per 1000 males.",
    10: "which rivers flow in andhra pradesh: Godavari, Krishna, Penna, Tungabhadra.",
    11: "who are famous leaders of andhra pradesh: Potti Sriramulu, N. T. Rama Rao (NTR), Y. S. Rajasekhara Reddy.",
    12: "what is the history of andhra pradesh: Ancient Satavahanas ruled, then Eastern Chalukyas, Kakatiyas, Vijayanagara Empire; became a separate state in 1956.",
    13: "what is the culture of andhra pradesh: Kuchipudi dance, Telugu literature, festivals like Sankranti, Ugadi, Bonalu, Bathukamma.",
    14: "what are tourist places in andhra pradesh: Tirupati, Amaravati, Visakhapatnam, Vijayawada, Araku Valley, Lepakshi, Srisailam.",
    15: "what is the economy of andhra pradesh: Agriculture, IT, pharmaceuticals, shipping, tourism, and industries.",
    16: "what are major industries in andhra pradesh: IT, pharmaceuticals, textiles, food processing, shipping.",
    17: "what is the main occupation in andhra pradesh: Agriculture, along with IT and industries.",
    18: "what is the climate of andhra pradesh: Tropical with hot summers, mild winters, monsoon rains.",
    19: "which are the major ports of andhra pradesh: Visakhapatnam, Krishnapatnam.",
    20: "what are important festivals in andhra pradesh: Sankranti, Ugadi, Bonalu, Bathukamma, Diwali.",
    21: "what are major crops in andhra pradesh: Rice, sugarcane, cotton, chillies, tobacco, groundnut.",
    22: "which mountains are in andhra pradesh: Eastern Ghats pass through the state.",
    23: "which wildlife sanctuaries are in andhra pradesh: Papikonda, Kambalakonda, Sri Venkateswara, Coringa.",
    24: "what is the transport system in andhra pradesh: Roads, railways, airports (Visakhapatnam, Vijayawada, Tirupati), seaports.",
    25: "how many airports are in andhra pradesh: Visakhapatnam, Vijayawada, Tirupati, Rajahmundry, Kadapa.",
    26: "what is the main religion in andhra pradesh: Hinduism majority, followed by Islam and Christianity.",
    27: "what are important temples in andhra pradesh: Tirupati Balaji, Srisailam, Kanaka Durga, Simhachalam.",
    28: "who is the first CM of andhra pradesh: Neelam Sanjiva Reddy.",
    29: "what is the official emblem of andhra pradesh: The emblem shows a wheel, plough and traditional symbols.",
    30: "what is the state animal of andhra pradesh: Blackbuck.",
    31: "what is the state bird of andhra pradesh: Indian roller (Blue Jay).",
    32: "what is the state flower of andhra pradesh: Jasmine.",
    33: "what is the state tree of andhra pradesh: Neem tree.",
    34: "which is the highest peak in andhra pradesh: Arma Konda in Eastern Ghats.",
    35: "which is the longest river in andhra pradesh: Godavari.",
    36: "which is the largest city in andhra pradesh: Visakhapatnam.",
    37: "which districts are in northern andhra pradesh: Srikakulam, Vizianagaram, Visakhapatnam.",
    38: "which districts are in southern andhra pradesh: Chittoor, Tirupati, Kadapa, Anantapur.",
    39: "what is the human development index in andhra pradesh: Moderate HDI, improving in recent years.",
    40: "which are famous educational institutions in andhra pradesh: Andhra University, IIT Tirupati, NIT Warangal (shared region).",
    41: "what is the major port city in andhra pradesh: Visakhapatnam.",
    42: "who are famous freedom fighters from andhra pradesh: Alluri Sitarama Raju, Potti Sriramulu.",
    43: "what is the traditional dress in andhra pradesh: Saree for women, dhoti and shirt for men.",
    44: "which is the most visited hill station in andhra pradesh: Araku Valley.",
    45: "what is the main cuisine in andhra pradesh: Rice, spicy curries, pulihora, pickles, Gongura.",
    46: "which industries are in Visakhapatnam: Shipping, IT, steel, heavy industry.",
    47: "which industries are in Vijayawada: Textiles, agriculture-based industries, trade.",
    48: "who are famous poets from andhra pradesh: Nannaya, Tikkana, Pothana.",
    49: "what is the main sport in andhra pradesh: Cricket and kabaddi.",
    50: "which is the famous dance of andhra pradesh: Kuchipudi.",
    51: "which districts are famous for tourism: Visakhapatnam, Chittoor, Kadapa, Anantapur.",
    52: "which districts are famous for temples: Tirupati, Srisailam, Vijayawada.",
    53: "which districts are famous for hill stations: Araku Valley, Horsley Hills.",
    54: "which district is most industrialized: Visakhapatnam.",
    55: "which district is famous for agriculture: Guntur, Krishna, Prakasam.",
    56: "which districts have major IT hubs: Visakhapatnam, Vijayawada, Tirupati.",
    57: "which districts are coastal: Visakhapatnam, East Godavari, West Godavari, Krishna, Guntur, Nellore.",
    58: "which districts are famous for rice cultivation: West Godavari, Krishna, Guntur.",
    59: "which districts are famous for chillies: Guntur, Kadapa, Prakasam.",
    60: "which districts are famous for tobacco: Prakasam, Guntur, Kurnool.",
    61: "which districts are famous for cotton: Kurnool, Anantapur.",
    62: "which districts are famous for sugarcane: Guntur, Krishna, West Godavari.",
    63: "which districts are famous for mangoes: Chittoor, Krishna, West Godavari.",
    64: "which districts are famous for handlooms: East Godavari, Krishna, Guntur.",
    65: "which districts are famous for fisheries: Visakhapatnam, East Godavari, Nellore.",
    66: "which districts are famous for forests: Visakhapatnam, Srikakulam, Chittoor.",
    67: "which districts are famous for wildlife sanctuaries: Visakhapatnam, East Godavari.",
    68: "which districts are famous for spices: Chittoor, Guntur, Kadapa.",
    69: "which districts are famous for temples architecture: Tirupati, Vijayawada, Srikalahasti.",
    70: "which districts are famous for Buddhist heritage: Amaravati, Guntur.",
    71: "which districts are famous for festivals: Tirupati (Brahmotsavam), Vijayawada (Kanaka Durga Navaratri).",
    72: "which districts are famous for handcrafts: Chittoor, Krishna, Guntur.",
    73: "which districts are famous for silk weaving: Kadapa, Chittoor.",
    74: "which districts are famous for IT parks: Visakhapatnam, Vijayawada, Tirupati.",
    75: "which districts are famous for steel and heavy industry: Visakhapatnam.",
    76: "which districts are famous for ports: Visakhapatnam, Krishnapatnam.",
    77: "which districts are famous for coconut cultivation: West Godavari, East Godavari, Krishna.",
    78: "which districts are famous for groundnuts: Anantapur, Kurnool.",
    79: "which districts are famous for banana cultivation: West Godavari, Krishna, Guntur.",
    80: "which districts are famous for tourism and heritage: Tirupati, Araku, Amaravati, Vijayawada.",
    81: "which districts are famous for hill ranges: Visakhapatnam, Chittoor.",
    82: "which districts are famous for scenic waterfalls: Visakhapatnam (Dumbriguda, Kambalakonda).",
    83: "which districts are famous for cultural festivals: Chittoor, Tirupati, Guntur.",
    84: "which districts are famous for pilgrimage: Tirupati, Srisailam, Vijayawada.",
    85: "which districts are famous for boat races: West Godavari, Krishna.",
    86: "which districts are famous for temples in Vijayawada: Kanaka Durga Temple, Undavalli Caves.",
    87: "which districts are famous for Buddhist sites: Amaravati, Guntur.",
    88: "which districts are famous for heritage forts: Chittoor, Kurnool, Nellore.",
    89: "which districts are famous for beaches: Visakhapatnam, Krishna, Nellore.",
    90: "which districts are famous for rivers: Godavari (East Godavari), Krishna (Krishna, Guntur).",
    91: "which districts are famous for dams: Srisailam, Nagarjuna Sagar, Polavaram.",
    92: "which districts are famous for wildlife: Visakhapatnam, Srikakulam, Chittoor.",
    93: "which districts are famous for hill temples: Tirupati, Srikalahasti.",
    94: "which districts are famous for heritage architecture: Amaravati, Vijayawada, Tirupati.",
    95: "which districts are famous for mango markets: Chittoor, Krishna, West Godavari.",
    96: "which districts are famous for cultural dance: Kuchipudi (Krishna district).",
    97: "which districts are famous for handloom sarees: Kadapa, Guntur, Chittoor.",
    98: "which districts are famous for craft villages: Chittoor, Guntur.",
    99: "which districts are famous for temples with gopurams: Tirupati, Vijayawada, Srikalahasti.",
    100: "which districts are famous for tourism destinations: Tirupati, Araku Valley, Amaravati, Vijayawada, Visakhapatnam."
}

# FIX: this function was missing entirely — the andhra_pradesh dict above
# existed but had no way to query it, making it dead data. Mirrors the
# same lookup pattern as tamil_nadu_info() for consistency.
def andhra_pradesh_info(query: str):
    return _find_info(query, andhra_pradesh)