
var app = new Vue({
    el: '#login',
    data: {
        message: '',
        token:  '',
        benchmark: {},
        error: '',
        algs: [],
        sel_algs: []
    },
    methods: {
        login: function(e) {
            var self = this;
            $.ajax(make_ajax_info('login', e)
                  ).done(function(data) {
                self.token = '';
                self.error = data['error'];

                if (!self.error) {
                    self.algs = data['algs'];
                    self.token = data['token'];
                    self.sel_algs = [];
                }
            }).fail(function(data) {
                self.error = data['error'];
            });
        },
        changeAlg: function(e) {
            var self = this;
            $.ajax(make_ajax_info('changeAlg', e)
            ).done(function(data) {
                self.error = data['error'];

                if (!self.error) {
                    self.algs = data['algs'];
                    self.sel_algs = [];
                }
            }).fail(function(data) {
                console.log('failed');
                console.log(data.responseJSON);
                var error = data.responseJSON['message'];
                self.error = '';

                for (name in error) {
                    self.error += name +': ' +error[name];
                }
            });
        }
    }
});
