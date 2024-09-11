export default class Logger {
    #create_msg(type = "msg", content = "empty") {
        let frag = document.createDocumentFragment();
        let div = document.createElement("div");
        div.classList.add(type);
        div.innerText = content;
        frag.appendChild(div);
        return frag;
    }

    success(enjectableElementRef, content) {
        let fragment = this.#create_msg('msg', content);
        if (enjectableElementRef.current) {
            enjectableElementRef.current.append(fragment);
        }

    }

    error(enjectableElementRef, content) {
        let fragment = this.#create_msg('error', content);
        if (enjectableElementRef.current) {
            enjectableElementRef.current.append(fragment);
        }

    }

    info(enjectableElementRef, content) {
        let fragment = this.#create_msg('info', content);
        if (enjectableElementRef.current) {
            enjectableElementRef.current.append(fragment);
        }

    }
    recommendation(enjectableElementRef, content) {
        let fragment = this.#create_msg('recom', content);
        if (enjectableElementRef.current) {
            enjectableElementRef.current.append(fragment);
        }

    }
}