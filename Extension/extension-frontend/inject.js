(function () {
    const existingApp = document.getElementById("react-sidebar-root");

    // ----------------------------------------------------------
    // If iframe already exists -> remove it (toggle off)
    // ----------------------------------------------------------
    if (existingApp) {
        existingApp.remove();
        const toggleBtn = document.getElementById("react-toggle-btn");
        if (toggleBtn) toggleBtn.remove();
        return;
    }

    // ----------------------------------------------------------
    // Otherwise -> inject it (toggle on)
    // ----------------------------------------------------------
    const root = document.createElement("div");
    root.id = "react-sidebar-root";
    document.body.appendChild(root);

    // 1. Container for iframe
    const container = document.createElement("div");
    container.style.cssText = `
        position: fixed;
        top: 100px;
        right: 100px;
        width: 400px;
        height: 700px;
        z-index: 999999;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        transform: translate3d(0, 0, 0);
        transition: opacity 0.3s ease-in-out, transform 0.3s ease-in-out;
        will-change: transform;
        opacity: 0;
    `;

    // 2. React iframe
    const iframe = document.createElement("iframe");
    iframe.src = chrome.runtime.getURL("index.html");
    iframe.style.cssText = `
        width: 100%;
        height: 100%;
        border: none;
        border-radius: 16px;
        background: #fff;
        overflow: hidden;
    `;

    // 3. Drag handle
    const dragHandle = document.createElement("div");
    dragHandle.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 40px;
        cursor: grab;
        background: transparent;
        z-index: 1000000;
    `;

    // 4. Restore last position
    let savedPos = JSON.parse(localStorage.getItem("iframePosition") || "{}");
    let startX = 0, startY = 0;
    let currentX = savedPos.x || 0;
    let currentY = savedPos.y || 0;
    let offsetX = currentX;
    let offsetY = currentY;
    container.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;

    // 5. Pointer-based smooth dragging
    let isDragging = false;

    const onPointerDown = (e) => {
        isDragging = true;
        dragHandle.setPointerCapture(e.pointerId);
        startX = e.clientX;
        startY = e.clientY;
        dragHandle.style.cursor = "grabbing";
        container.style.transition = "none";
        container.style.boxShadow = "none";
    };

    const onPointerMove = (e) => {
        if (!isDragging) return;
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        currentX = offsetX + dx;
        currentY = offsetY + dy;
        container.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
    };

    const onPointerUp = (e) => {
        if (!isDragging) return;
        isDragging = false;
        dragHandle.releasePointerCapture(e.pointerId);
        dragHandle.style.cursor = "grab";
        container.style.transition = "transform 0.2s ease-out, opacity 0.3s ease-in-out";
        container.style.boxShadow = "0 4px 12px rgba(0,0,0,0.25)";
        offsetX = currentX;
        offsetY = currentY;
        localStorage.setItem("iframePosition", JSON.stringify({ x: currentX, y: currentY }));
    };

    dragHandle.addEventListener("pointerdown", onPointerDown);
    dragHandle.addEventListener("pointermove", onPointerMove);
    dragHandle.addEventListener("pointerup", onPointerUp);
    dragHandle.addEventListener("pointercancel", onPointerUp);

    // 6. Build & append
    container.appendChild(iframe);
    container.appendChild(dragHandle);
    root.appendChild(container);

    // 7. Floating toggle (in-page button, optional)
    const toggleBtn = document.createElement("img");
    toggleBtn.src = chrome.runtime.getURL("icons.png");
    toggleBtn.id = "react-toggle-btn";
    toggleBtn.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 200px;
        height: 100px;
        cursor: pointer;
        z-index: 9999999;
    `;
    document.body.appendChild(toggleBtn);

    let open = false;
    toggleBtn.onclick = () => {
        open = !open;
        if (open) {
            container.style.opacity = "1";
            container.style.transform = `translate3d(${currentX}px, ${currentY}px, 0) scale(1)`;
        } else {
            container.style.opacity = "0";
            container.style.transform = `translate3d(${currentX}px, ${currentY}px, 0) scale(0.95)`;
        }
    };
})();
