const header = document.querySelector("#site-header");
const menuToggle = document.querySelector(".menu-toggle");
const navigation = document.querySelector("#main-nav");
const revealItems = document.querySelectorAll(".reveal");

const updateHeader = () => {
    header.classList.toggle("scrolled", window.scrollY > 24);
};

const closeMenu = () => {
    menuToggle.setAttribute("aria-expanded", "false");
    menuToggle.setAttribute("aria-label", "Ouvrir le menu");
    navigation.classList.remove("open");
    document.body.classList.remove("menu-open");
};

menuToggle.addEventListener("click", () => {
    const isOpen = menuToggle.getAttribute("aria-expanded") === "true";
    menuToggle.setAttribute("aria-expanded", String(!isOpen));
    menuToggle.setAttribute("aria-label", isOpen ? "Ouvrir le menu" : "Fermer le menu");
    navigation.classList.toggle("open", !isOpen);
    document.body.classList.toggle("menu-open", !isOpen);
});

navigation.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeMenu));
window.addEventListener("scroll", updateHeader, { passive: true });
updateHeader();

const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.14 });

revealItems.forEach((item, index) => {
    item.style.transitionDelay = `${Math.min(index % 4, 3) * 90}ms`;
    revealObserver.observe(item);
});

document.querySelector("#current-year").textContent = new Date().getFullYear();

const stageEl = document.querySelector("[data-portfolio-stage]");
const spotlightItems = stageEl ? Array.from(stageEl.querySelectorAll("[data-spotlight-item]")) : [];
const subjectDots = Array.from(document.querySelectorAll("[data-subject-dot]"));

if (stageEl && spotlightItems.length > 0) {
    const SUBJECT_DURATION_MS = 6000;
    const SLIDE_STEP_MS = 2000;
    const TITLE_WORD_MS = 90;
    const SUMMARY_WORD_MS = 100;

    let activeSubjectIdx = 0;
    let subjectTimer = null;
    let slideTimer = null;
    let typingTimers = [];
    let isPaused = false;

    const clearAllTimers = () => {
        if (subjectTimer) clearTimeout(subjectTimer);
        if (slideTimer) clearInterval(slideTimer);
        typingTimers.forEach((id) => clearTimeout(id));
        typingTimers = [];
        subjectTimer = null;
        slideTimer = null;

        spotlightItems.forEach((item) => {
            item.querySelectorAll("[data-type-meta], [data-type-title], [data-type-summary]").forEach((el) => {
                el.classList.remove("is-typing");
            });
        });
    };

    const writeWordByWord = (el, rawText, startDelay, stepMs, onComplete) => {
        if (!el) {
            if (onComplete) onComplete();
            return;
        }

        const cleanText = (rawText || "").trim();
        el.textContent = "";
        el.classList.remove("is-typing");

        if (!cleanText) {
            if (onComplete) onComplete();
            return;
        }

        const words = cleanText.split(/\s+/);

        const startId = setTimeout(() => {
            el.classList.add("is-typing");

            words.forEach((word, index) => {
                const wordId = setTimeout(() => {
                    el.textContent = el.textContent ? `${el.textContent} ${word}` : word;

                    if (index === words.length - 1) {
                        const endId = setTimeout(() => {
                            el.classList.remove("is-typing");
                            if (onComplete) onComplete();
                        }, 180);
                        typingTimers.push(endId);
                    }
                }, index * stepMs);

                typingTimers.push(wordId);
            });
        }, startDelay);

        typingTimers.push(startId);
    };

    const startImageStripForItem = (itemEl) => {
        const strip = itemEl.querySelector("[data-slides-strip]");
        const panels = strip ? Array.from(strip.querySelectorAll("[data-slide-panel]")) : [];
        const dots = Array.from(itemEl.querySelectorAll("[data-img-dot]"));

        if (!strip || panels.length <= 1) {
            if (strip) strip.style.transform = "translateX(0%)";
            return;
        }

        let slideIdx = 0;
        strip.style.transform = "translateX(0%)";
        dots.forEach((d, i) => d.classList.toggle("is-active", i === 0));

        slideTimer = setInterval(() => {
            if (isPaused) return;
            slideIdx = (slideIdx + 1) % panels.length;
            strip.style.transform = `translateX(-${slideIdx * 100}%)`;
            dots.forEach((d, i) => d.classList.toggle("is-active", i === slideIdx));
        }, SLIDE_STEP_MS);
    };

    const activateSubject = (nextIdx, immediate = false) => {
        clearAllTimers();

        const prevItem = spotlightItems[activeSubjectIdx];
        const nextItem = spotlightItems[nextIdx];

        if (prevItem && prevItem !== nextItem) {
            prevItem.classList.remove("is-active");
            prevItem.classList.add("is-exiting");
            setTimeout(() => prevItem.classList.remove("is-exiting"), 500);
        }

        spotlightItems.forEach((el, idx) => {
            if (idx !== nextIdx) {
                el.classList.remove("is-active");
            }
        });

        activeSubjectIdx = nextIdx;
        nextItem.classList.remove("is-exiting");
        nextItem.classList.add("is-active");

        subjectDots.forEach((dot, idx) => {
            dot.classList.toggle("is-active", idx === nextIdx);
        });

        const metaEl = nextItem.querySelector("[data-type-meta]");
        const titleEl = nextItem.querySelector("[data-type-title]");
        const summaryEl = nextItem.querySelector("[data-type-summary]");

        const rawMeta = nextItem.dataset.meta || "";
        const rawTitle = nextItem.dataset.title || "";
        const rawSummary = nextItem.dataset.summary || "";

        if (metaEl) metaEl.textContent = "";
        if (titleEl) titleEl.textContent = "";
        if (summaryEl) summaryEl.textContent = "";

        if (metaEl && rawMeta) {
            writeWordByWord(metaEl, rawMeta, 30, 35, () => {
                writeWordByWord(titleEl, rawTitle, 40, TITLE_WORD_MS, () => {
                    writeWordByWord(summaryEl, rawSummary, 60, SUMMARY_WORD_MS);
                });
            });
        } else {
            writeWordByWord(titleEl, rawTitle, 50, TITLE_WORD_MS, () => {
                writeWordByWord(summaryEl, rawSummary, 70, SUMMARY_WORD_MS);
            });
        }

        startImageStripForItem(nextItem);

        if (spotlightItems.length > 1 && !immediate) {
            subjectTimer = setTimeout(() => {
                if (!isPaused) {
                    const followingIdx = (activeSubjectIdx + 1) % spotlightItems.length;
                    activateSubject(followingIdx, false);
                }
            }, SUBJECT_DURATION_MS);
        }
    };

    subjectDots.forEach((dot) => {
        dot.addEventListener("click", () => {
            const targetIdx = Number(dot.dataset.subjectDot);
            if (!Number.isNaN(targetIdx) && targetIdx >= 0 && targetIdx < spotlightItems.length) {
                activateSubject(targetIdx, false);
            }
        });
    });

    stageEl.addEventListener("mouseenter", () => {
        isPaused = true;
    });

    stageEl.addEventListener("mouseleave", () => {
        isPaused = false;
        if (spotlightItems.length > 1 && !subjectTimer) {
            subjectTimer = setTimeout(() => {
                const followingIdx = (activeSubjectIdx + 1) % spotlightItems.length;
                activateSubject(followingIdx, false);
            }, 1400);
        }
    });

    activateSubject(0, false);
}