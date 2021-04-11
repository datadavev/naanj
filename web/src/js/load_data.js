import moment from 'moment';
export let NAANS_erc = {};
export let NAANS = [];

function processNaanList(data) {
    NAANS_erc = data.erc;
    console.log(NAANS_erc);
    for (let naa of data.naa) {
        let dd = new Date(naa["when"]);
        let entry = {
            abbrev : naa.who.abbrev,
            who: naa.who.literal,
            what: naa.what,
            when: moment(dd).format("YYYY-MM-DD"),
            //when: dd,
            url: naa["where"].url,
            status: naa["where"].status,
            checked: naa["where"].checked,
            msg: naa["where"].msg
        }
        NAANS.push(entry)
    }
    console.log(NAANS.length)
    return NAANS;
}

export function loadNaans() {
    let url = "/assets/naanj.json";
    return fetch(url)
        .then(response => response.json())
        .then(data => processNaanList(data))
}