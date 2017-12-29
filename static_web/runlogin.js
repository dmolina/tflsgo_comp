
var app = new Vue({
    el: '#login',
    data: {
        token:  '',
        benchmark: {},
        error: '',
        error_load: '',
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
        store: function(e) {
                var self = this;
                $.ajax(make_ajax_info('store', e)
                      ).done(function(data) {
                          self.error_load = data['error'];

                          if (!self.error) {
                              var new_algs = data['new_algs'];
                              self.algs = self.algs.concat(new_algs);
                              var new_algs_str = data['new_algs_str'];
                              self.message = 'Algorithms \'' +new_algs_str +'\' written without error';
                          }
                      }).fail(function(data) {
                          self.error_load = process_fail(data);
                      });

        }
    }
});
