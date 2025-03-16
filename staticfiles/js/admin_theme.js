// Add custom CSS to the admin page
document.addEventListener('DOMContentLoaded', function() {
    // Add Font Awesome
    const fontAwesome = document.createElement('link');
    fontAwesome.rel = 'stylesheet';
    fontAwesome.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css';
    document.head.appendChild(fontAwesome);
    
    // Add custom CSS
    const customCSS = document.createElement('link');
    customCSS.rel = 'stylesheet';
    customCSS.href = '/static/admin/css/custom_admin.css';
    document.head.appendChild(customCSS);
    
    // Add theme toggle button
    const userTools = document.querySelector('#user-tools');
    if (userTools) {
        const themeToggle = document.createElement('div');
        themeToggle.className = 'theme-toggle';
        themeToggle.innerHTML = `
            <button id="theme-toggle" aria-label="Toggle dark mode">
                <i class="fas fa-moon dark-icon"></i>
                <i class="fas fa-sun light-icon" style="display: none;"></i>
            </button>
        `;
        userTools.insertBefore(themeToggle, userTools.firstChild);
        
        // Add theme toggle functionality
        const toggleButton = document.getElementById('theme-toggle');
        const darkIcon = document.querySelector('.dark-icon');
        const lightIcon = document.querySelector('.light-icon');
        
        // Check for saved theme preference or use preferred color scheme
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
            document.documentElement.setAttribute('data-theme', 'dark');
            darkIcon.style.display = 'none';
            lightIcon.style.display = 'inline';
        }
        
        // Toggle theme
        toggleButton.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            
            if (currentTheme === 'dark') {
                document.documentElement.setAttribute('data-theme', 'light');
                darkIcon.style.display = 'inline';
                lightIcon.style.display = 'none';
                localStorage.setItem('theme', 'light');
            } else {
                document.documentElement.setAttribute('data-theme', 'dark');
                darkIcon.style.display = 'none';
                lightIcon.style.display = 'inline';
                localStorage.setItem('theme', 'dark');
            }
        });
    }
    
    // Transform the app list into a grid
    const appList = document.querySelector('.app-list');
    if (appList) {
        // Already using our custom template
        return;
    }
    
    // If we're on the index page, transform the default app list
    const contentMain = document.querySelector('#content-main');
    if (contentMain && window.location.pathname.endsWith('/admin/')) {
        // Create app dashboard
        const appDashboard = document.createElement('div');
        appDashboard.className = 'app-dashboard';
        
        // Create app list
        const newAppList = document.createElement('div');
        newAppList.className = 'app-list';
        
        // Get all app modules
        const appModules = contentMain.querySelectorAll('.app');
        
        // Transform each app module
        appModules.forEach(function(appModule) {
            const appItem = document.createElement('div');
            appItem.className = 'app-item';
            
            // Get app name
            const appName = appModule.querySelector('caption a').textContent.trim();
            
            // Create app header
            const appHeader = document.createElement('h2');
            
            // Add icon based on app name
            let iconClass = 'fas fa-cube';
            if (appName.includes('Authentication') || appName.includes('Auth')) {
                iconClass = 'fas fa-users';
            } else if (appName.includes('Clients')) {
                iconClass = 'fas fa-building';
            } else if (appName.includes('Sales')) {
                iconClass = 'fas fa-chart-line';
            } else if (appName.includes('Documents')) {
                iconClass = 'fas fa-file-alt';
            } else if (appName.includes('Dashboard')) {
                iconClass = 'fas fa-tachometer-alt';
            } else if (appName.includes('Expenses')) {
                iconClass = 'fas fa-receipt';
            } else if (appName.includes('Purchases')) {
                iconClass = 'fas fa-shopping-cart';
            } else if (appName.includes('Banking')) {
                iconClass = 'fas fa-university';
            } else if (appName.includes('Reports')) {
                iconClass = 'fas fa-chart-bar';
            } else if (appName.includes('Access Control')) {
                iconClass = 'fas fa-lock';
            } else if (appName.includes('Registration')) {
                iconClass = 'fas fa-user-plus';
            } else if (appName.includes('People')) {
                iconClass = 'fas fa-address-book';
            } else if (appName.includes('Project')) {
                iconClass = 'fas fa-tasks';
            } else if (appName.includes('Admin')) {
                iconClass = 'fas fa-cog';
            }
            
            appHeader.innerHTML = `<i class="${iconClass}"></i> ${appName}`;
            appItem.appendChild(appHeader);
            
            // Create model list
            const modelList = document.createElement('ul');
            modelList.className = 'model-list';
            
            // Get all model rows
            const modelRows = appModule.querySelectorAll('tr');
            
            // Transform each model row
            modelRows.forEach(function(modelRow) {
                const modelItem = document.createElement('li');
                
                // Get model name and links
                const modelName = modelRow.querySelector('th a') ? 
                    modelRow.querySelector('th a').textContent.trim() : 
                    modelRow.querySelector('th').textContent.trim();
                
                const modelAdminUrl = modelRow.querySelector('th a') ? 
                    modelRow.querySelector('th a').getAttribute('href') : null;
                
                const modelAddUrl = modelRow.querySelector('.addlink') ? 
                    modelRow.querySelector('.addlink').getAttribute('href') : null;
                
                // Create model item
                let modelItemHTML = '';
                
                if (modelAdminUrl) {
                    modelItemHTML += `<a href="${modelAdminUrl}">${modelName}</a>`;
                } else {
                    modelItemHTML += modelName;
                }
                
                if (modelAddUrl) {
                    modelItemHTML += `
                        <a href="${modelAddUrl}" class="addlink">
                            <span class="action-badge add">Add</span>
                        </a>
                    `;
                }
                
                if (modelAdminUrl) {
                    modelItemHTML += `
                        <a href="${modelAdminUrl}" class="changelink">
                            <span class="action-badge change">View</span>
                        </a>
                    `;
                }
                
                modelItem.innerHTML = modelItemHTML;
                modelList.appendChild(modelItem);
            });
            
            appItem.appendChild(modelList);
            newAppList.appendChild(appItem);
        });
        
        appDashboard.appendChild(newAppList);
        
        // Transform recent actions
        const recentActions = contentMain.querySelector('#recent-actions-module');
        if (recentActions) {
            recentActions.className = 'recent-actions';
            
            // Transform action list items
            const actionItems = recentActions.querySelectorAll('.actionlist li');
            actionItems.forEach(function(actionItem) {
                // Determine action type
                let actionType = '';
                let actionBadge = '';
                
                if (actionItem.classList.contains('addlink')) {
                    actionType = 'add';
                    actionBadge = 'Add';
                } else if (actionItem.classList.contains('changelink')) {
                    actionType = 'change';
                    actionBadge = 'Edit';
                } else if (actionItem.classList.contains('deletelink')) {
                    actionType = 'delete';
                    actionBadge = 'Delete';
                }
                
                if (actionType) {
                    // Get content type and object
                    const actionContent = actionItem.textContent.trim();
                    const contentTypeParts = actionContent.split(':');
                    
                    if (contentTypeParts.length > 1) {
                        const contentType = contentTypeParts[0].trim();
                        const objectRepr = contentTypeParts[1].trim();
                        
                        // Create new action item HTML
                        actionItem.innerHTML = `
                            <span class="action-badge ${actionType}">${actionBadge}</span>
                            <span class="mini">${contentType}</span>
                            ${actionItem.innerHTML.includes('<a') ? actionItem.innerHTML : objectRepr}
                        `;
                    }
                }
            });
            
            appDashboard.appendChild(recentActions);
        }
        
        // Replace content
        contentMain.innerHTML = '';
        contentMain.appendChild(appDashboard);
    }
}); 