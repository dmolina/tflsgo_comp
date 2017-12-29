
var app = new Vue({
    el: '#login',
    data: {
        token:  '',
        message: '',
        benchmark: {},
        bench_user: {},
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
            self.message = '';

            $.ajax(make_ajax_info('store', e)
                  ).done(function(data) {
                      self.error_load = data['error'];

                      if (!self.error_load) {
                          var new_algs = data['new_algs'];
                          self.algs = self.algs.concat(new_algs);
                          var new_algs_str = data['new_algs_str'];
                          self.message = 'Algorithms \'' +new_algs_str +'\' written without error';
                      }
                  }).fail(function(data) {
                      self.error_load = process_fail(data);
                  });
        },
        check_delete: function() {
            var self = this;
            var result = confirm(self.sel_algs.toString() +' will be deleted. Are you sure?');

            if (result) {
                data = {'algs': self.sel_algs, 'token': self.token};
                $.ajax({
                    url: '/delete',
                    type: 'POST',
                    data: '',
                    dataType: 'json',
                    cache: false,
                    contentType: false,
                    processData: false
                }).done(function(data) {
                });
            }
        }
    }
});
