document.getElementById('user-preferences').addEventListener('submit', function(event) {
    event.preventDefault();   
    
    const seat = document.getElementById('seat').value;   
    const meal = document.getElementById('meal').value;  
    
     
    fetch('/api/preferences', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'   
        },
        body: JSON.stringify({
            user_id: '123',   
            preferences: {
                seat: seat,   
                meal: meal    
            }
        })
    })
    .then(response => response.json())   
    .then(data => {
        alert(data.message);   
    });
});
