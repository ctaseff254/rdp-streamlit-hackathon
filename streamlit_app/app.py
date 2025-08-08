import traceback

import streamlit as st

from _logger import log, logging_config


@st.cache_resource
def _configure_logging() -> None:
    logging_config()
    log.info("Starting application...")


def main() -> None:
    dashboard = st.Page("pages/dashboard.py", title="Dashboard", icon=":material/home:", default=True)

    pg = st.navigation(
        {
            "App": [dashboard],
        }
    )

    pg.run()


if __name__ == "__main__":
    try:
        _configure_logging()
        main()
    except Exception as e:
        log.critical(traceback.format_exc())
        raise e
