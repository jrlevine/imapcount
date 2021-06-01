%rebase('dcbase.tpl', name="Messages sorted by hours")
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
  <canvas id="hourChart"></canvas>
</div>

<script>

const data = {
  labels: [ {{hournames}} ],
  datasets: [{
%if mls:
    label: 'Message counts by hour from {{mls}}',
%else:
    label: 'Message counts by hour (UTC)',
%end
    data: [ {{hourdata}}],
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
        var ctx = document.getElementById('hourChart');
        var myLine = new Chart(ctx, config );
};

function beforePrintHandler () {
    for (var id in Chart.instances) {
        Chart.instances[id].resize();
    }
}

window.onbeforeprint = beforePrintHandler;
</script>
