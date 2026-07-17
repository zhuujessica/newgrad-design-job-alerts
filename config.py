# Edit these lists any time -- matching is case-insensitive substring matching,
# so "product designer" also matches "Staff Product Designer", "Product Designer I", etc.
# A listing notifies only when it matches at least one entry from COMPANIES
# AND at least one entry from ROLE_KEYWORDS.

COMPANIES = [
    "Google", "Apple", "Microsoft", "Amazon", "Meta", "Nvidia", "Netflix", "Adobe",
    "Salesforce", "Airbnb", "Uber", "Figma", "Spotify", "Stripe", "Shopify", "Atlassian",
    "LinkedIn", "Pinterest", "Dropbox", "Slack", "Intuit", "SAP", "Oracle", "Databricks",
    "Notion", "Canva", "Discord", "Reddit", "DoorDash", "Instacart", "Coinbase",
    "Robinhood", "Asana", "Zoom", "Lyft", "Twilio", "Squarespace", "Etsy", "Datadog",
    "Cloudflare", "Roblox", "Duolingo", "Affirm", "Klarna", "Grammarly", "Webflow",
    "Airtable", "Miro", "Linear", "Ramp", "Yelp", "eBay", "PayPal", "Wayfair",
    "Booking.com", "Expedia", "DocuSign", "Zillow", "Vimeo", "SoundCloud",
    "Warner Bros. Discovery", "Disney", "Samsung", "Sony", "LG", "Tesla", "Rivian",
    "IBM", "Intel", "AMD", "Cisco", "ServiceNow", "Workday", "Splunk", "MongoDB",
    "Snowflake", "GitLab", "GitHub", "Okta", "CrowdStrike", "Twitch", "Epic Games",
    "Riot Games", "Unity", "Niantic", "Waymo", "Cruise", "Zoox", "SpaceX", "OpenAI",
    "Anthropic", "Perplexity", "Vercel", "Supabase", "Toast", "Chime", "SoFi", "Plaid",
]

ROLE_KEYWORDS = [
    "Product Designer", "Junior Product Designer", "Associate Product Designer",
    "Entry Level Product Designer", "Product Designer I", "Product Designer 1",
    "UX Designer", "Junior UX Designer", "Associate UX Designer",
    "Entry Level UX Designer", "UX Designer I", "UX Designer 1", "UX/UI Designer",
    "UI/UX Designer", "UI Designer", "Junior UI Designer", "Associate UI Designer",
    "User Experience Designer", "Junior User Experience Designer",
    "User Interface Designer", "Interaction Designer", "Junior Interaction Designer",
    "Associate Interaction Designer", "Visual Designer", "Junior Visual Designer",
    "Associate Visual Designer", "Digital Designer", "Junior Digital Designer",
    "UX Design Intern", "Product Design Intern", "UX/Product Designer",
    "Design Associate", "Associate Designer", "New Grad Product Designer",
    "New Grad UX Designer", "Product Designer New Grad",
]

# Install the free "ntfy" app (iOS/Android) and subscribe to this exact topic name
# to receive push notifications. Anyone who knows this topic name can publish to
# it or read it, so keep it private -- it's randomized to avoid guessing.
NTFY_TOPIC = "newgrad-design-jz-af908949"
