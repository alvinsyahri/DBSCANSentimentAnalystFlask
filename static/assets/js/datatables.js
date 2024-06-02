$(document).ready(function () {
    function initializeDataTable(tableId) {
        $(tableId).DataTable({
            "scrollX": true,
            "language": {
                "search": "",
                "searchPlaceholder": "Search...",
                "decimal": ",",
                "thousands": ".",
            },
            "lengthMenu": [5, 10, 15, 20, 25, 50, 100], // Set the row length options
            "pageLength": 5
        });

        $('.dataTables_filter input[type="search"]').css({
            "marginBottom": "10px"
        });
    }

    initializeDataTable("#myTable");
    initializeDataTable("#myTable1");
    initializeDataTable("#myTable2");
    initializeDataTable("#myTable3");
});