$(document).ready(function() {
    // Attach click event to Generate Numbers button
    $('#generate-btn').click(function() {
      $.ajax({
        url: '/generate',
        type: 'POST',
        success: function(data) {
          alert(data.message);
        },
        error: function(xhr, status, error) {
          console.error(error);
        }
      });
    });
  
    // Attach click event to Show Results button
    $('#results-btn').click(function() {
      $.ajax({
        url: '/results',
        type: 'GET',
        success: function(data) {
          var resultHtml = '<h2>Results</h2>';
          resultHtml += '<p>Largest Number: ' + data.largest + '</p>';
          resultHtml += '<p>Smallest Number: ' + data.smallest + '</p>';
          $('#result-box').html(resultHtml);
        },
        error: function(xhr, status, error) {
          console.error(error);
        }
      });
    });
  });
  