const fs = require('fs');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;

const html = fs.readFileSync('datavis_capstone.html', 'utf-8');

const dom = new JSDOM(html, {
    url: "http://localhost/",
    runScripts: "dangerously",
    resources: "usable"
});

dom.window.addEventListener('error', (event) => {
    console.error("DOM Window Error:", event.error);
});

// We can execute datavis_capstone_app.js directly or wait for it to load
// Since resources="usable", script tags will be fetched. But local file fetch might be tricky.
// We can manually load the script to be safe:

setTimeout(() => {
    try {
        const appScript = fs.readFileSync('datavis_capstone_app.js', 'utf-8');
        // Define dependencies manually
        dom.window.eval(`
            var CodeMirror = { fromTextArea: function() { return { setValue: function(){}, getValue: function(){} }; } };
            var PyPlayAuth = { user: null };
            var Chart = function() { return { destroy: function(){} }; };
        `);
        dom.window.eval(appScript);
        
        // Wait a bit for DOMContentLoaded / init
        setTimeout(() => {
            const title = dom.window.document.getElementById('lesson-title').textContent;
            const concept = dom.window.document.getElementById('lesson-concept').textContent;
            console.log("Title after init:", title);
            console.log("Concept after init:", concept);
        }, 1000);
        
    } catch(err) {
        console.error("Manual Script Error:", err);
    }
}, 1000);
