// Global back button disabling for the entire experiment
// This prevents participants from going back to previous pages

(function() {
    // Disable browser back button
    history.pushState(null, null, location.href);
    window.onpopstate = function(event) {
        history.pushState(null, null, location.href);
        // Optionally show a message
        alert('{{ tr("You cannot go back during the experiment. Please continue forward.") }}');
    };
    
    // Also prevent backspace key from going back
    document.addEventListener('keydown', function(e) {
        // Backspace key (but allow in input fields)
        if (e.key === 'Backspace' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
            e.preventDefault();
        }
    });
})();

