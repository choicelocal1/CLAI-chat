(function() {
    // Widget loader configuration
    var config = {{ config|safe }};
    
    // Create global namespace
    window.CLAIChat = window.CLAIChat || {};
    
    // Initialize function
    window.CLAIChat.init = function(options) {
        // Merge configurations
        var mergedConfig = Object.assign({}, config, options);
        
        // Create widget container if not specified
        if (!options.containerId) {
            var container = document.createElement('div');
            container.id = 'clai-chat-widget-container';
            document.body.appendChild(container);
            mergedConfig.containerId = container.id;
        }
        
        // Load widget styles
        var styleLink = document.createElement('link');
        styleLink.rel = 'stylesheet';
        styleLink.href = config.apiUrl + '/widget/' + config.chatbotId + '/styles.css';
        document.head.appendChild(styleLink);
        
        // Load main widget script
        var script = document.createElement('script');
        script.src = config.apiUrl + '/widget/' + config.chatbotId + '/bundle.js';
        script.async = true;
        script.onload = function() {
            // Initialize widget with configuration
            window.CLAIChat.Widget.init(mergedConfig);
        };
        document.head.appendChild(script);
        
        // Store configuration
        window.CLAIChat.config = mergedConfig;
    };
})();
