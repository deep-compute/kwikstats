var main = (function() {
    var _ws = null;
    var _output_div_id = null;
    var counter = Counter();
    var charts = null;

    var init = function(ws_uri, output_div_id) {
        _output_div_id = output_div_id;

        _ws = new WebSocket(ws_uri);
        _ws.onopen = _on_open;
        _ws.onclose = _on_close;
        _ws.onmessage = _on_message;
        _ws.onerror = _on_error;
    };

    var make_absolute_uri = function(path) {
        var loc = window.location, new_uri;

        if (loc.protocol === "https:") {
            new_uri = "wss:";
        } else {
            new_uri = "ws:";
        }

        new_uri += "//" + loc.host;
        new_uri += "/ws";
        return new_uri;
    };

    var _on_open = function (evt) {
        console.log(evt);
    }

    var _on_message = function (evt) {
        var data = JSON.parse(evt.data);
        counter.submit_counts(data[0], data[1]);
        updateCharts();
    }

    var _on_close = function (evt) {
        console.log(evt);
    }

    var _on_error = function (evt) {
        console.log(evt);
    }

    var updateCharts = function() {
        if (charts) charts.remove();

		charts = d3.select('body')
			.selectAll('.horizon')
			.data(_.map(counter.evts, function(k) {
                return {title: k, values: counter.data[k]};
            }))
			.enter()
            .append('div')
            .attr('class', 'horizon')
            .each(function(d) {
                d3.horizonChart().title(d.title).call(this, d.values);
            });
    }

    return {
        init: init,
        counter: counter,
        make_absolute_uri: make_absolute_uri
    };
})();
