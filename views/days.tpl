%rebase('dcbase.tpl', name="Messages sorted by day of week")
{{!boilerplate}}
<center>
%if defined('kvetch') and kvetch:
    <p>{{!kvetch}}</p>
%end
</center>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.3.2/chart.min.js" 
 integrity="sha512-VCHVc5miKoln972iJPvkQrUYYq7XpxXzvqNfiul1H4aZDwGBGC0lq373KNleaB2LpnC2a/iNfE5zoRYmB4TRDQ==" 
 crossorigin="anonymous" referrerpolicy="no-referrer">
</script>
<div>
  <canvas id="dayChart"></canvas>
</div>

<script>

const data = {
  labels: [ {{!daynames}} ],
  datasets: [{
    label: 'Message counts by day of week',
    data: [ {{daydata}}],
    borderWidth: 2,
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderColor: 'rgba(0,0,0,1)'
  }]
};

const config = {
  type: 'bar',
  data: data,
  options: {
  indexAxis: 'y',
    scales: {
      x: {
        beginAtZero: true
      }
    }
  },
};

window.onload = function() {
        var ctx = document.getElementById('dayChart');
        var myLine = new Chart(ctx, config );
};
</script>
