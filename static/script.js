// static/script.js

// Global variables
let selectedProducts = [];
let currentResults = [];
let currentSort = 'price-low';

// DOM Elements
document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme
    initTheme();
    
    // Load history
    loadHistory();
    
    // Event listeners
    document.getElementById('searchBtn').addEventListener('click', performSearch);
    document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') performSearch();
    });
    
    document.getElementById('sortSelect').addEventListener('change', function(e) {
        currentSort = e.target.value;
        sortAndDisplayResults();
    });
    
    document.getElementById('compareBtn').addEventListener('click', openCompareModal);
    
    // Popular search tags
    document.querySelectorAll('.popular-tag').forEach(tag => {
        tag.addEventListener('click', function() {
            document.getElementById('searchInput').value = this.dataset.search;
            performSearch();
        });
    });
    
    // Theme toggle
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    
    // Website checkboxes
    document.querySelectorAll('.website-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (document.getElementById('searchInput').value) {
                performSearch();
            }
        });
    });
});

// Theme functions
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('#themeToggle i');
    if (theme === 'dark') {
        icon.className = 'fas fa-sun';
    } else {
        icon.className = 'fas fa-moon';
    }
}

// Search function
async function performSearch() {
    const product = document.getElementById('searchInput').value.trim();
    if (!product) {
        showNotification('Please enter a product name', 'error');
        return;
    }
    
    // Get selected websites
    const websites = [];
    document.querySelectorAll('.website-checkbox:checked').forEach(cb => {
        websites.push(cb.value);
    });
    
    if (websites.length === 0) {
        showNotification('Please select at least one website', 'error');
        return;
    }
    
    // Show loading
    document.getElementById('loadingOverlay').style.display = 'flex';
    
    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ product, websites })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentResults = data.results;
            selectedProducts = [];
            updateSelectedCount();
            
            // Display results
            sortAndDisplayResults();
            updateSummaryCards(data.results);
            
            // Load history
            loadHistory();
            
            showNotification(`Found ${data.count} products!`, 'success');
        } else {
            showNotification(data.error || 'Search failed', 'error');
        }
    } catch (error) {
        console.error('Search error:', error);
        showNotification('Failed to search products', 'error');
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

// Sort and display results
function sortAndDisplayResults() {
    let sortedResults = [...currentResults];
    
    switch(currentSort) {
        case 'price-low':
            sortedResults.sort((a, b) => (a.price || Infinity) - (b.price || Infinity));
            break;
        case 'price-high':
            sortedResults.sort((a, b) => (b.price || 0) - (a.price || 0));
            break;
        case 'rating':
            sortedResults.sort((a, b) => {
                const ratingA = parseFloat(a.rating) || 0;
                const ratingB = parseFloat(b.rating) || 0;
                return ratingB - ratingA;
            });
            break;
    }
    
    displayProducts(sortedResults);
}

// Display products in grid
function displayProducts(products) {
    const grid = document.getElementById('productsGrid');
    
    if (!products || products.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-search"></i>
                <h3>No products found</h3>
                <p>Try searching for something else</p>
            </div>
        `;
        document.getElementById('resultsCount').textContent = '';
        return;
    }
    
    document.getElementById('resultsCount').textContent = `(${products.length})`;
    
    let html = '';
    products.forEach((product, index) => {
        const isSelected = selectedProducts.some(p => p.link === product.link);
        const isBestPrice = index === 0; // First product has best price
        
        html += `
            <div class="product-card">
                ${isBestPrice ? '<div class="product-badge best-price">Best Price</div>' : ''}
                <div class="product-image">
                    <img src="${product.image || 'https://via.placeholder.com/300x200?text=Product'}" 
                         alt="${product.title}"
                         onerror="this.src='https://via.placeholder.com/300x200?text=No+Image'">
                    <input type="checkbox" 
                           class="product-checkbox" 
                           ${isSelected ? 'checked' : ''}
                           onchange="toggleProductSelection(${JSON.stringify(product).replace(/"/g, '&quot;')})">
                </div>
                <div class="product-info">
                    <h3 class="product-title">${product.title}</h3>
                    <span class="product-website">${product.website}</span>
                    <div class="product-price">Rs. ${product.price ? product.price.toLocaleString() : 'N/A'}</div>
                    <div class="product-rating">
                        <div class="stars">
                            ${generateStars(product.rating)}
                        </div>
                        <span class="rating-value">${product.rating || 'N/A'}</span>
                    </div>
                    <div class="product-actions">
                        <a href="${product.link}" target="_blank" class="view-link">View Product</a>
                        <button class="add-compare ${isSelected ? 'active' : ''}" 
                                onclick="toggleProductSelection(${JSON.stringify(product).replace(/"/g, '&quot;')})">
                            <i class="fas ${isSelected ? 'fa-check' : 'fa-plus'}"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    grid.innerHTML = html;
}

// Generate star rating HTML
function generateStars(rating) {
    if (!rating || rating === 'N/A') return '';
    
    const numRating = parseFloat(rating);
    if (isNaN(numRating)) return '';
    
    const fullStars = Math.floor(numRating);
    const halfStar = numRating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
    
    let stars = '';
    for (let i = 0; i < fullStars; i++) stars += '<i class="fas fa-star"></i>';
    if (halfStar) stars += '<i class="fas fa-star-half-alt"></i>';
    for (let i = 0; i < emptyStars; i++) stars += '<i class="far fa-star"></i>';
    
    return stars;
}

// Toggle product selection for comparison
function toggleProductSelection(product) {
    const index = selectedProducts.findIndex(p => p.link === product.link);
    
    if (index === -1) {
        if (selectedProducts.length >= 5) {
            showNotification('You can compare up to 5 products at a time', 'warning');
            return;
        }
        selectedProducts.push(product);
    } else {
        selectedProducts.splice(index, 1);
    }
    
    updateSelectedCount();
    
    // Update checkbox and button states
    sortAndDisplayResults();
}

// Update selected products count
function updateSelectedCount() {
    document.getElementById('selectedCount').textContent = selectedProducts.length;
    
    const compareBtn = document.getElementById('compareBtn');
    if (selectedProducts.length >= 2) {
        compareBtn.disabled = false;
        compareBtn.style.opacity = '1';
    } else {
        compareBtn.disabled = true;
        compareBtn.style.opacity = '0.5';
    }
}

// Update summary cards
function updateSummaryCards(products) {
    const websites = [...new Set(products.map(p => p.website))];
    const avgPrice = products.reduce((sum, p) => sum + (p.price || 0), 0) / products.length;
    const bestPrice = Math.min(...products.map(p => p.price || Infinity));
    
    const cards = document.getElementById('summaryCards');
    cards.innerHTML = `
        <div class="summary-card">
            <div class="summary-icon">
                <i class="fas fa-store"></i>
            </div>
            <div class="summary-info">
                <h4>Stores</h4>
                <div class="value">${websites.length}</div>
            </div>
        </div>
        <div class="summary-card">
            <div class="summary-icon">
                <i class="fas fa-box"></i>
            </div>
            <div class="summary-info">
                <h4>Products</h4>
                <div class="value">${products.length}</div>
            </div>
        </div>
        <div class="summary-card">
            <div class="summary-icon">
                <i class="fas fa-tag"></i>
            </div>
            <div class="summary-info">
                <h4>Avg Price</h4>
                <div class="value">Rs. ${avgPrice.toFixed(0)}</div>
            </div>
        </div>
        <div class="summary-card">
            <div class="summary-icon">
                <i class="fas fa-star"></i>
            </div>
            <div class="summary-info">
                <h4>Best Price</h4>
                <div class="value">Rs. ${bestPrice}</div>
            </div>
        </div>
    `;
}

// Load search history
async function loadHistory() {
    try {
        const response = await fetch('/history');
        const searches = await response.json();
        
        const grid = document.getElementById('historyGrid');
        
        if (!searches || searches.length === 0) {
            grid.innerHTML = `
                <div class="empty-state" style="grid-column: 1/-1;">
                    <i class="fas fa-history"></i>
                    <h3>No search history</h3>
                    <p>Your recent searches will appear here</p>
                </div>
            `;
            return;
        }
        
        let html = '';
        searches.forEach(search => {
            const date = new Date(
                search.timestamp.slice(0, 4) + '-' +
                search.timestamp.slice(4, 6) + '-' +
                search.timestamp.slice(6, 8) + 'T' +
                search.timestamp.slice(9, 11) + ':' +
                search.timestamp.slice(11, 13) + ':' +
                search.timestamp.slice(13, 15)
            );
            
            html += `
                <div class="history-card">
                    <div class="history-time">${date.toLocaleString()}</div>
                    <div class="history-products">${search.count} products found</div>
                    <button class="download-btn" onclick="downloadHistory('${search.filename}')">
                        <i class="fas fa-download"></i> Download
                    </button>
                </div>
            `;
        });
        
        grid.innerHTML = html;
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// Download history file
function downloadHistory(filename) {
    window.location.href = `/download/${filename}`;
}

// Open compare modal
function openCompareModal() {
    if (selectedProducts.length < 2) {
        showNotification('Please select at least 2 products to compare', 'warning');
        return;
    }
    
    // Create comparison table
    let compareHtml = `
        <div class="compare-modal">
            <div class="compare-header">
                <h2>Product Comparison</h2>
                <button onclick="closeCompareModal()">&times;</button>
            </div>
            <div class="compare-table">
                <table>
                    <tr>
                        <th>Feature</th>
                        ${selectedProducts.map(p => `<th>${p.website}</th>`).join('')}
                    </tr>
                    <tr>
                        <td>Product</td>
                        ${selectedProducts.map(p => `<td>${p.title}</td>`).join('')}
                    </tr>
                    <tr>
                        <td>Price</td>
                        ${selectedProducts.map(p => `<td>Rs. ${p.price?.toLocaleString() || 'N/A'}</td>`).join('')}
                    </tr>
                    <tr>
                        <td>Rating</td>
                        ${selectedProducts.map(p => `<td>${p.rating || 'N/A'}</td>`).join('')}
                    </tr>
                    <tr>
                        <td>Link</td>
                        ${selectedProducts.map(p => `<td><a href="${p.link}" target="_blank">View</a></td>`).join('')}
                    </tr>
                </table>
            </div>
        </div>
    `;
    
    // Add modal to body
    const modal = document.createElement('div');
    modal.className = 'compare-modal-overlay';
    modal.innerHTML = compareHtml;
    document.body.appendChild(modal);
}

// Close compare modal
function closeCompareModal() {
    document.querySelector('.compare-modal-overlay').remove();
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 3000;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .compare-modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 4000;
        animation: fadeIn 0.3s ease;
    }
    
    .compare-modal {
        background: var(--card-bg);
        border-radius: 1rem;
        max-width: 90%;
        max-height: 90%;
        overflow: auto;
        animation: slideUp 0.3s ease;
    }
    
    .compare-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    .compare-header h2 {
        color: var(--text-primary);
    }
    
    .compare-header button {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: var(--text-secondary);
    }
    
    .compare-table {
        padding: 1.5rem;
        overflow-x: auto;
    }
    
    .compare-table table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .compare-table th,
    .compare-table td {
        padding: 1rem;
        border: 1px solid var(--border-color);
        color: var(--text-primary);
    }
    
    .compare-table th {
        background: var(--primary-color);
        color: white;
        font-weight: 600;
    }
    
    .compare-table td:first-child {
        font-weight: 600;
        background: var(--light-bg);
    }
    
    .notification {
        pointer-events: none;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideUp {
        from {
            transform: translateY(20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
`;

document.head.appendChild(style);
