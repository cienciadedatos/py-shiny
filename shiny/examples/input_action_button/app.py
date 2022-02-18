from shiny import *
import numpy as np
import matplotlib.pyplot as plt

app_ui = ui.page_fluid(
    ui.input_slider("n", "Number of observations", 0, 1000, 500),
    ui.input_action_button("go", "Go!", class_="btn-success"),
    ui.output_plot("plt"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output()
    @render_plot(alt="A histogram")
    # Use event() to invalidate the plot only when the button is pressed
    # (not when the slider is changed)
    @event(lambda: input.go, ignore_none=False)
    def plt():
        np.random.seed(19680801)
        x = 100 + 15 * np.random.randn(input.n())
        fig, ax = plt.subplots()
        ax.hist(x, bins=30, density=True)
        return fig


app = App(app_ui, server)