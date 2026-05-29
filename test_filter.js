function run() {
    const data = [
        { Order: "101", Product: "Mouse", Price: 25, Qty: 2 },
        { Order: "102", Product: "Keyboard", Price: null, Qty: 1 },
        { Order: "103", Product: "Monitor", Price: 150, Qty: 0 },
        { Order: "104", Product: "Headset", Price: 45, Qty: 3 },
        { Order: "105", Product: "Webcam", Price: null, Qty: 5 }
    ];
    let filteredData = data.filter(row => {
        let val = row['Qty'];
        let compareVal = Number(1);
        let rowVal = Number(val);
        return rowVal >= compareVal;
    });
    console.log(filteredData.length);
}
run();
