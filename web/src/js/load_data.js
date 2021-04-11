//import moment from 'moment';
export let NAANS = [];
const NAANS_SOURCE = "https://raw.githubusercontent.com/datadavev/naanj/main/data/naanj.json";

function processNaanList(data) {
    let meta = data.erc
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
        NAANS.push(entry)
    }
    meta.num_errors = error_count;
    meta.naanj_source = NAANS_SOURCE;
    let event = new CustomEvent("naans-load", {
        detail: {
            meta: meta
        }
    });
    window.dispatchEvent(event);
    console.log(NAANS.length)
    return NAANS;
}

export function loadNaans() {
    return fetch(NAANS_SOURCE)
        .then(response => response.json())
        .then(data => processNaanList(data))
}