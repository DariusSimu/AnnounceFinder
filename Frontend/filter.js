// ----------- Exchange rates -----------
let exchangeRates = {};

async function fetchExchangeRates() {
    try {
        const res  = await fetch('/exchange-rates');
        const data = await res.json();
        exchangeRates = data.rates;
        exchangeRates['EUR'] = 1.0;
    } catch (e) {
        console.warn('Could not fetch exchange rates:', e);
        exchangeRates = { EUR: 1.0, RON: 4.97, GBP: 0.85 };
    }
}

// ----------- Price parsing and conversion ----------
function parsePrice(priceStr) {
    if (!priceStr || priceStr === 'N/A') return null;
    const match = priceStr.match(/([\d.,]+)\s*([A-Z]+)/);
    if (!match) return null;
    const value    = parseFloat(match[1].replace(',', '.'));
    const currency = match[2];
    return { value, currency };
}

function toEUR(value, currency) {
    if (currency === 'EUR') return value;
    if (currency === 'RON') return value / (exchangeRates['RON'] || 4.97);
    if (currency === 'GBP') return value / (exchangeRates['GBP'] || 0.85);
    return value;
}

function convertPrice(priceStr, targetCurrency) {
    const parsed = parsePrice(priceStr);
    if (!parsed) return null;
    const inEUR     = toEUR(parsed.value, parsed.currency);
    const rate      = exchangeRates[targetCurrency] || 1.0;
    const converted = inEUR * rate;
    return `${converted.toFixed(2)} ${targetCurrency}`;
}

// ----------- Filter state and logic -----------
let filterState = {
    sort:              'none',
    displayCurrency:   'none',
    conditions:        [],
    platforms:         []
};

function updateFilterState() {
    filterState.sort            = document.getElementById('filter-sort').value;
    filterState.displayCurrency = document.getElementById('filter-currency').value;
    filterState.conditions      = [...document.querySelectorAll('.filter-condition:checked')].map(c => c.value);
    filterState.platforms       = [...document.querySelectorAll('.filter-platform:checked')].map(p => p.value);
}

// ---------- Apply filters and sorting to listings ----------
function applyFilters(listings) {
    updateFilterState();
    let result = [...listings];

    // Filter by condition
    if (filterState.conditions.length === 0) {
        result = [];
    } else {
        result = result.filter(r =>
            r.condition === 'BOTH' || filterState.conditions.includes(r.condition)
        );
    }

    // Filter by platform
    if (filterState.platforms.length > 0) {
        result = result.filter(r => filterState.platforms.includes(r.platform));
    }

    // Sort
    if (filterState.sort === 'az') {
        result.sort((a, b) => a.title.localeCompare(b.title));
    } else if (filterState.sort === 'za') {
        result.sort((a, b) => b.title.localeCompare(a.title));
    } else if (filterState.sort === 'price-asc' || filterState.sort === 'price-desc') {
        result.sort((a, b) => {
            const pa = parsePrice(a.price);
            const pb = parsePrice(b.price);
            if (!pa) return 1;
            if (!pb) return -1;
            const ea = toEUR(pa.value, pa.currency);
            const eb = toEUR(pb.value, pb.currency);
            return filterState.sort === 'price-asc' ? ea - eb : eb - ea;
        });
    }

    return result;
}

// ----------- Display currency -----------
function getDisplayPrice(priceStr) {
    if (filterState.displayCurrency === 'none') return priceStr;
    const converted = convertPrice(priceStr, filterState.displayCurrency);
    return converted || priceStr;
}

// ----------- Platform checkboxes -----------
function buildPlatformCheckboxes(listings) {
    const platforms = [...new Set(listings.map(r => r.platform))];
    const container = document.getElementById('filter-platforms');
    container.innerHTML = '';
    platforms.forEach(p => {
        const label = document.createElement('label');
        label.className = 'filter-checkbox';
        label.innerHTML = `
            <input type="checkbox" class="filter-platform" value="${p}" checked onchange="onFilterChange()"/>
            ${p}
        `;
        container.appendChild(label);
    });
}

// ----------- Called on any filter change -----------
function onFilterChange() {
    if (typeof currentListings !== 'undefined') {
        renderListings(applyFilters(currentListings));
    }
}