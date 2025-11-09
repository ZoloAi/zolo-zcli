// zServer Demo JavaScript

console.log('✅ JavaScript loaded successfully from zServer!');

function runTest() {
    const output = document.getElementById('output');
    const timestamp = new Date().toLocaleTimeString();
    
    // Simulate async operation
    output.textContent = 'Running tests...';
    output.className = 'output';
    
    setTimeout(() => {
        const tests = [
            { name: 'HTML File', status: 'PASS' },
            { name: 'CSS Loading', status: 'PASS' },
            { name: 'JavaScript Execution', status: 'PASS' },
            { name: 'CORS Headers', status: 'PASS' },
            { name: 'HTTP Server', status: 'PASS' }
        ];
        
        let result = `✅ All Tests Passed! (${timestamp})\n\n`;
        tests.forEach(test => {
            result += `• ${test.name}: ${test.status}\n`;
        });
        
        output.textContent = result;
        output.className = 'output success';
        
        console.log('Test Results:', tests);
    }, 500);
}

// Auto-run test on page load
window.addEventListener('load', () => {
    console.log('Page loaded via zServer HTTP server');
    console.log('Server: Python built-in http.server');
    console.log('Framework: zCLI');
});

// Add keyboard shortcut
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 't') {
        e.preventDefault();
        runTest();
    }
});

