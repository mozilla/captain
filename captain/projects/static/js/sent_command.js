;(function($) {
    'use strict';

    $(document.body).on('show.bs.collapse', '#shove-logs .not-loaded', function(e) {
        var $panel = $(this);
        var $logContent = $panel.find('.log-content');
        $.get($panel.data('logUrl'), function(log) {
            $logContent.text(log);
        });

        // Mark as loaded so we don't re-load.
        $panel.removeClass('not-loaded');
    });
}(jQuery));
