var base_url = "http://localhost:8000";

var app = new Vue({
    el: '#app',
    data: {
        benchmarks: {},
        alg_name: '',
        selected: -1,
        available_algs: {},
        algs: [],
        error: '',
        dimension: ''
    },
    mounted: function() {
        var self = this;
        $.ajax({
            url: base_url +'/benchmarks',
            method: 'GET',
            success: function(data) {
                self.benchmarks = data['benchmarks'];
            }
        });
    },
    methods: {
        onChangedBenchmark: function() {
            var self = this;
            var dimensions = self.benchmarks[self.selected].dimensions;

            if (dimensions.length==1) {
                self.dimension = dimensions[0];
            }
            $.ajax({
                url: base_url +'/algs/' +self.selected,
                method: 'GET',
                sucess: function(data) {
                    self.available_algs = data['algs'];
                    self.error = data['error'];
                }
            });
        },
        sendData: function(e) {
            var self = this;
            e.preventDefault();
            var formData = new FormData(e.target);

            $.ajax({
                url: base_url +'/compare',
                type: 'POST',
                data: formData,
                dataType: 'json',
                cache: false,
                contentType: false,
                processData: false
            }).done(function(data) {
                if (data['error']) {
                    self.error = data['error'];
                    $("label#file").focus();
                }
            })
                .fail(function(data){
                    console.log(data);
                error = data.responseJSON.message;

                for (name in error) {
                    self.error += error[name];
                }
                });
        }
    }

});
