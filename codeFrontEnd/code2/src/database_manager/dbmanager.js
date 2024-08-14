export class dbManager {
    #execution_routine(callBackWithDbObject) {
        const request = window.indexedDB.open("database", 3);
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            db.onerror = (event) => {
                console.error("Error loading database:", event.target.errorCode);
            };
            // Create an objectStore for storing code
            this.#codeDatabaseObjectCreation(db);
            // more dbs can be created here
        };
        request.onsuccess = (event) => {
            const db = event.target.result;
            callBackWithDbObject(db);
        };
        request.onerror = (event) => {
            console.error("Database error:", event.target.errorCode);
        };
    }

    /**
     * this function creates an a database object
     * @param {*} db the db instance
     */
    #codeDatabaseObjectCreation(db)
    {   
        const objectStore = db.createObjectStore("codestored", {
            keyPath: "id",
            autoIncrement: true
        });
        objectStore.createIndex("code", "code", { unique: false });
        objectStore.createIndex("date", "date", { unique: false });
    }

    /**
     * this function retrieves data from some objectName
     * the function throws an error if the objectName doesn't exist
     * @param {String} objectName the name of the db object
     * @param {Function} callBackWithData a callback function that is going to receive the data
     * @param {number} count the number of elements the resultwill return , -1 to get all
     */
    retrieveData(objectName, count, callBackWithData)
    {
        this.#execution_routine((db) => {
            const transaction = db.transaction([objectName], "readonly");
            const objectStore = transaction.objectStore(objectName);
            const request = objectStore.openCursor();
            const data = [];
            request.onsuccess = (event) => {
                let localCount = 0;
                const cursor = event.target.result;
                if (count >= 0)
                {
                    if (cursor && localCount < count) {
                        data.push(cursor.value);
                        cursor.continue();
                        localCount++;
                    } else {
                        callBackWithData(data);
                    }
                }
                else{
                    if (cursor) {
                        data.push(cursor.value);
                        cursor.continue();
                    } else {
                        callBackWithData(data);
                    }
                }
            };
            request.onerror = (event) => {
                console.error("Cursor error:", event.target.errorCode);
            };
        });
    }
    /**
     * this function inserts a new record for some object in a database
     * the function throws an error if the objectName does not exist
     * @param {string} objectName 
     * @param {object} Data 
     */
    insertData(objectName, Data) {
        this.#execution_routine((db) => {
            const transaction = db.transaction([objectName], "readwrite");
            const objectStore = transaction.objectStore(objectName);
            const request = objectStore.add(Data);
            request.onsuccess = (event) => {
                console.log("insertData operation successful", event.target.result);
            };
            request.onerror = (event) => {
                console.error("Error executing insertData:", event.target.errorCode);
            };
        });
    }
    /**
     * this function clears an object
     * the function throws an error if the objectName doesn't exist
     * @param {*} objectName the name of the db object
     * @param {*} optionalCallbackPostClear  an optional callback for after the clear
     */
    clearObject(objectName, optionalCallbackPostClear)
    {
        this.#execution_routine((db) => {
            const transaction = db.transaction([objectName], "readwrite");
            const objectStore = transaction.objectStore(objectName);
            const request = objectStore.clear();
            request.onsuccess = (event) => {
                console.log("insertData operation successful", event.target.result);
                if (optionalCallbackPostClear)
                {
                    optionalCallbackPostClear();
                }
            };
            request.onerror = (event) => {
                console.error("Error executing insertData:", event.target.errorCode);
            };
        });
    }
}
