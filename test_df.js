class DataFrame {
    constructor(data, name = "dataset") {
        this.data = data;
        this.name = name;
        this.columns = data.length > 0 ? Object.keys(data[0]) : [];
    }
    
    get length() {
        return this.data.length;
    }

    filter(colName, operator, value) {
        let filteredData = this.data.filter(row => {
            let val = row[colName];
            let compareVal = Number(value);
            if (isNaN(compareVal)) {
                compareVal = value;
            }
            let rowVal = Number(val);
            if (isNaN(rowVal)) {
                rowVal = val;
            }
            if (operator === '>=') return rowVal >= compareVal;
            if (operator === '<=') return rowVal <= compareVal;
            if (operator === '>') return rowVal > compareVal;
            if (operator === '<') return rowVal < compareVal;
            if (operator === '==') return rowVal == compareVal;
            if (operator === '!=') return rowVal != compareVal;
            return true;
        });
        return new DataFrame(filteredData, this.name);
    }
}

function run() {
    const data = [
        { Order: "101", Product: "Mouse", Price: 25, Qty: 2 },
        { Order: "102", Product: "Keyboard", Price: null, Qty: 1 },
        { Order: "103", Product: "Monitor", Price: 150, Qty: 0 },
        { Order: "104", Product: "Headset", Price: 45, Qty: 3 },
        { Order: "105", Product: "Webcam", Price: null, Qty: 5 }
    ];
    let df = new DataFrame(data);
    df = df.filter("Qty", ">=", 1);
    console.log(df.length);
}
run();
