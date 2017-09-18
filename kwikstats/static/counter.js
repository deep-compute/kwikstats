var Counter = function() {
    var last_ts = 0;
    var n_datapoints = 0;
    var max_datapoints = 100;
    var data = {};
    var evts = [];

    var submit_counts = function(ts, counts) {
        if (last_ts == 0) {
            _.forEach(counts, function(count, evt) {
                var evt_data = _.get(data, evt);
                if (evt_data != undefined) {
                    evt_data.push(count);
                } else {
                    data[evt] = [count];
                }

                evts.push(evt);
            });
        } else {
            // For newly seen evts, add series
            _.forEach(counts, function(count, evt) {
                if (_.get(data, evt) == undefined) {
                    data[evt] = new Array(n_datapoints);
                    _.fill(data[evt], 0);
                    evts.push(evt);
                }
            });

            // Pad data series with zero for intermediate
            // seconds for which we got no data
            _.forEach(_.range(last_ts+1, ts), function(k) {
                _.forEach(data, function(series, evt) {
                    series.push(0);
                });

                n_datapoints++;
            });

            // Add current second data to the series
            // and push 0 for those events that don't
            // have any updates in this second
            _.forEach(data, function(series, evt) {
                var v = _.get(counts, evt);
                if (v != undefined) {
                    series.push(v);
                } else {
                    series.push(0);
                }
            });
        }

        last_ts = ts;
        n_datapoints++;

        ensureDataPointLength();
    };

    var set_max_data_points = function(n) {
        max_datapoints = n;
    };

    var ensureDataPointLength = function() {
        if (n_datapoints == max_datapoints) return;

        if (n_datapoints > max_datapoints) {
            var diff = n_datapoints - max_datapoints;
            _.forEach(data, function(series, evt) {
                data[evt] = _.drop(series, diff);
            });
        } else {
            var diff = max_datapoints - n_datapoints;
            _.forEach(data, function(series, evt) {
                _.forEach(_.range(0, diff), function(i) {
                    series.unshift(0);
                });
            });
        }

        n_datapoints = max_datapoints;
    }

    return {
        submit_counts: submit_counts,
        set_max_data_points: set_max_data_points,
        data: data,
        evts: evts
    };
};
