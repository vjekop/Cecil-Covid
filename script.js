// Import jQuery (assuming you're using a CDN)
// <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>

$(document).ready(function() {
    $('#search-form').on('submit', function(e) {
        e.preventDefault();
        
        $.ajax({
            url: '/search',
            method: 'POST',
            data: $(this).serialize(),
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    $('#result-zipcode').text($('#zipcode').val());
                    $('#result-date').text($('#date').val());
                    $('#result-cases').text(response.cases);
                    $('#result').show();
                    $('#result-graph').attr('src', response.graph_url).show();
                    $('#table-date').text($('#date').val());
                    $('#table-cases').text(response.cases);
                    $('#result-table').show();
                } else {
                    alert(response.message);
                }
            },
            error: function() {
                alert('An error occurred while processing your request.');
            }
        });
    });
});