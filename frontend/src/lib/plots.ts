// Bounding boxes (in the 600x420 viewBox of /dummy-land.svg) for each of the
// 4 dummy plots, used to render a cropped/zoomed "location on map" view and
// to draw a highlight outline around the relevant plot.
export interface PlotBBox {
  x: number;
  y: number;
  w: number;
  h: number;
  polygon: [number, number][];
}

export const PLOT_BBOXES: Record<string, PlotBBox> = {
  "1": {
    x: 20,
    y: 10,
    w: 260,
    h: 200,
    polygon: [
      [30, 40],
      [220, 20],
      [260, 150],
      [120, 190],
      [40, 140],
    ],
  },
  "2": {
    x: 270,
    y: 20,
    w: 230,
    h: 200,
    polygon: [
      [280, 30],
      [480, 60],
      [470, 200],
      [320, 220],
    ],
  },
  "3": {
    x: 40,
    y: 210,
    w: 240,
    h: 200,
    polygon: [
      [60, 220],
      [260, 240],
      [240, 390],
      [50, 380],
    ],
  },
  "4": {
    x: 290,
    y: 230,
    w: 270,
    h: 190,
    polygon: [
      [300, 240],
      [520, 260],
      [540, 400],
      [320, 400],
    ],
  },
};
