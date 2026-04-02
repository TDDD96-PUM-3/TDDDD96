// Data derived from https://gs.statcounter.com/os-market-share/desktop/worldwide/2023
// And https://gs.statcounter.com/os-market-share/mobile/worldwide/2023
// And https://gs.statcounter.com/platform-market-share/desktop-mobile-tablet/worldwide/2023
// For the month of December 2023

export const test = [
  {
    label: "Counterfeits",
    value: 6769,
  },
  {
    label: "Non-counterfeits",
    value: 3331,
  },
];

export const test1 = [
  {
    label: "Counterfeits", value: 50,
  },
  {
    label: "Non-counterfeits", value: 300,
  }
];

export const test2 = [
  {
    label: "Counterfeits", value: 6767,
  },
  {
    label: "Non-counterfeits", value: 3333,
  },
];

export const test3 = [
  {
    label: "Counterfeits", value: 6868,
  },
  {
    label: "Non-counterfeits", value: 3232,
  },
]

export const valueFormatter = (item) => `${item.value}%`;
