//import moment from 'moment';
export let NAANS = [];
const NAANS_SOURCE = "https://raw.githubusercontent.com/datadavev/naanj/main/data/naanj.json";

const stat_messages = {
    '-1': "TLS error without validation",
    '0': "Client was unable to establish a connection",
    '200': "OK",
    '400': "Bad Request",
    '401': "Unauthorized",
    '403': "Forbidden",
    '404': "Not Found",
    '406': "Not Acceptable",
    '429': "Too many requests",
    '500': "Internal Server Error",
    '502': "Bad Gateway",
    '503': "Service Unavailable",
}

function processNaanList(data) {
    let meta = data.erc;
    let stats = {};
    meta.when = moment(meta.when).format("YYYY-MM-DD");
    let error_count = 0
    for (let naa of data.naa) {
        let dd = new Date(naa["when"]);
        let entry = {
            abbrev : naa.who.abbrev,
            who: naa.who.literal,
            what: naa.what,
            when: moment(dd).format("YYYY-MM-DD"),
            url: naa["where"].url,
            status: naa["where"].status,
            checked: naa["where"].checked,
            msg: naa["where"].msg
        }
        if (entry.status !== 200) {
            error_count += 1;
        }
        stats[entry.status] = (stats[entry.status] || 0) + 1;
        NAANS.push(entry)
    }
    let astats = [];
    for (let s in stats) {
        astats.push( [s, stats[s], (stat_messages[s] || "")]);
    }
    meta.num_errors = error_count;
    meta.naanj_source = NAANS_SOURCE;
    let event = new CustomEvent("naans-load", {
        detail: {
            meta: meta,
            stats: stats,
            astats: astats
        }
    });
    window.dispatchEvent(event);
    window.stats = stats;
    console.log(NAANS.length)
    return NAANS;
}

export function loadNaans() {
    return fetch(NAANS_SOURCE)
        .then(response => response.json())
        .then(data => processNaanList(data))
}

