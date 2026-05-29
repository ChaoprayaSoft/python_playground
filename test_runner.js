class DataFrame {
    constructor(data, name = "dataset") {
        this.data = data;
        this.name = name;
        this.columns = Object.keys(data[0]);
    }
    get length() {
        return this.data.length;
    }
    dropna(options) {
        return createDataFrameProxy(new DataFrame(this.data));
    }
    filter(colName, operator, value) {
        let filteredData = this.data.filter(row => {
            let val = row[colName];
            let compareVal = Number(value);
            let rowVal = Number(val);
            if (operator === '>=') return rowVal >= compareVal;
            return true;
        });
        return createDataFrameProxy(new DataFrame(filteredData, this.name));
    }
}
const createDataFrameProxy = (dfInstance) => {
    return new Proxy(dfInstance, {
        get(target, prop) {
            if (prop in target) {
                return target[prop];
            }
            return null;
        }
    });
};

const sandbox = {
    pd: {
        read_csv: (filename) => {
            const data = [
                { Order: "101", Product: "Mouse", Price: 25, Qty: 2 },
                { Order: "102", Product: "Keyboard", Price: null, Qty: 1 },
                { Order: "103", Product: "Monitor", Price: 150, Qty: 0 },
                { Order: "104", Product: "Headset", Price: 45, Qty: 3 },
                { Order: "105", Product: "Webcam", Price: null, Qty: 5 }
            ];
            return createDataFrameProxy(new DataFrame(data));
        }
    },
    len: (x) => x.length,
    print: (x) => console.log("PRINT:", x)
};

const jsCode = `
var df = pd.read_csv('dirty_sales.csv')
df.dropna(subset=['Price'], inplace=true)
var df = df.filter("Qty", ">=", 1)
print(len(df))
`;

const AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;
const runner = new AsyncFunction('sandbox', `
    with (sandbox) {
        ${jsCode}
    }
`);

runner(sandbox).catch(e => console.error(e));
