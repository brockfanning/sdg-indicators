// Map configuration specifically for the United States.

var sdg_indicators = sdg_indicators || {};

sdg_indicators.getMapConfig = function() {
  return {
    region_ids: {
      'AL': '01',
      'AK': '02',
      'AZ': '04',
      'AR': '05',
      'CA': '06',
      'CO': '08',
      'CT': '09',
      'DE': '10',
      'DC': '11',
      'FL': '12',
      'GA': '13',
      'HI': '15',
      'ID': '16',
      'IL': '17',
      'IN': '18',
      'IA': '19',
      'KS': '20',
      'KY': '21',
      'LA': '22',
      'ME': '23',
      'MD': '24',
      'MA': '25',
      'MI': '26',
      'MN': '27',
      'MS': '28',
      'MO': '29',
      'MT': '30',
      'NE': '31',
      'NV': '32',
      'NH': '33',
      'NJ': '34',
      'NM': '35',
      'NY': '36',
      'NC': '37',
      'ND': '38',
      'OH': '39',
      'OK': '40',
      'OR': '41',
      'PA': '42',
      'RI': '44',
      'SC': '45',
      'SD': '46',
      'TN': '47',
      'TX': '48',
      'UT': '49',
      'VT': '50',
      'VA': '51',
      'WA': '53',
      'WV': '54',
      'WI': '55',
      'WY': '56',
      'AS': '60',
      'FM': '64',
      'GU': '66',
      'MH': '68',
      'MP': '69',
      'PW': '70',
      'PR': '72',
      'UM': '74',
      'VI': '78'
    },
    region_labels: {
      "AL": "Alabama",
      "AK": "Alaska",
      "AS": "American Samoa",
      "AZ": "Arizona",
      "AR": "Arkansas",
      "CA": "California",
      "CO": "Colorado",
      "CT": "Connecticut",
      "DE": "Delaware",
      "DC": "District Of Columbia",
      "FM": "Federated States Of Micronesia",
      "FL": "Florida",
      "GA": "Georgia",
      "GU": "Guam",
      "HI": "Hawaii",
      "ID": "Idaho",
      "IL": "Illinois",
      "IN": "Indiana",
      "IA": "Iowa",
      "KS": "Kansas",
      "KY": "Kentucky",
      "LA": "Louisiana",
      "ME": "Maine",
      "MH": "Marshall Islands",
      "MD": "Maryland",
      "MA": "Massachusetts",
      "MI": "Michigan",
      "MN": "Minnesota",
      "MS": "Mississippi",
      "MO": "Missouri",
      "MT": "Montana",
      "NE": "Nebraska",
      "NV": "Nevada",
      "NH": "New Hampshire",
      "NJ": "New Jersey",
      "NM": "New Mexico",
      "NY": "New York",
      "NC": "North Carolina",
      "ND": "North Dakota",
      "MP": "Northern Mariana Islands",
      "OH": "Ohio",
      "OK": "Oklahoma",
      "OR": "Oregon",
      "PW": "Palau",
      "PA": "Pennsylvania",
      "PR": "Puerto Rico",
      "RI": "Rhode Island",
      "SC": "South Carolina",
      "SD": "South Dakota",
      "TN": "Tennessee",
      "TX": "Texas",
      "UT": "Utah",
      "VT": "Vermont",
      "VI": "Virgin Islands",
      "VA": "Virginia",
      "WA": "Washington",
      "WV": "West Virginia",
      "WI": "Wisconsin",
      "WY": "Wyoming"
    },
    geojson_path: 'https://d3js.org/us-10m.v1.json',
    geojson_d3_callback: function(data) {
      return topojson.feature(data, data.objects.states).features;
    }
  };
}
