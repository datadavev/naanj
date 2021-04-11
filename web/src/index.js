import moment from 'moment';
import { loadNaans } from '@/js/load_data'

window.moment = moment

// Test import of an asset
// import webpackLogo from '@/images/webpack-logo.svg'

// Test import of styles
import '@/styles/index.scss'
//import 'tabulator-tables/dist/css/tabulator_simple.css'

import Tabulator from 'tabulator-tables'

Tabulator.prototype.extendModule("keybindings", "bindings", {
     "scrollPageDown": "34"
});

// create Tabulator on DOM element with id "example-table"
let table = new Tabulator('#example-table', {
  height: '50%', // set height of table (in CSS or here), this enables the Virtual DOM and improves render speed dramatically (can be any valid css height value)
  data: [], // assign data to table
  layout: 'fitColumnsStretch', // fit columns to width of table (optional)
  //columnMaxWidth: 300,
  //pagination: "local",
  //paginationSize: 25,
  //paginationSizeSelector:[10, 25, 50, true],
  selectable: 1,
  columns: [
    // Define Table Columns
    { title: 'ID', field: 'abbrev', frozen: true, headerFilter:"input",
      headerTooltip:"Organization name acronym"
    },
    { title: 'What', field: 'what', frozen: true, headerFilter:"input",
      headerTooltip: "NAAN"
    },
    { title: 'Who', field: 'who', headerFilter:"input", tooltip:true,
      headerTooltip: "Organization name"
    },
    {
      title: 'When',
      field: 'when',
      sorter: 'date',
      sorterParams: {
        format:"YYYY-MM-DD"
      },
      hozAlign: 'center',
      headerFilter:'input',
      headerTooltip: 'Date registered'
    },
    { title: 'URL', field: 'url', headerFilter:"input",
      formatter: "link",
      formatterParams: {
        target:"_blank"
      }
    },
    { title: 'Status', field: 'status', headerFilter:true},
    { title: 'Msg', field: 'msg' }
  ],
  rowClick: function (e, row) {
    // trigger an alert message when the row is clicked
    //alert('Row ' + row.getData().id + ' Clicked!!!!')
  },
  rowFormatter: function(row) {
    var data = row.getData();
    if (data.status != 200){
      row.getElement().style.color = "#FF3333";
    }
  }
});

loadNaans().then(data => table.setData(data));
