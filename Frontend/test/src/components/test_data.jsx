// Data derived from https://gs.statcounter.com/os-market-share/desktop/worldwide/2023
// And https://gs.statcounter.com/os-market-share/mobile/worldwide/2023
// And https://gs.statcounter.com/platform-market-share/desktop-mobile-tablet/worldwide/2023
// For the month of December 2023

export const desktopOS = [
  {
    label: "Counterfeits",
    value: 70,
  },
  {
    label: "Non-counterfeits",
    value: 30,
  },
];

export const test = [
  {
    label: "test1", value: 67,
  },
  {
    label: "test2", value: 33,
  }
];

export const test2 = [
  {
    label: "test1", value: 67,
  },
  {
    label: "test2", value: 33,
  },
  {
    label: "test3", value: 45,
  },
  {
    label: "test4", value: 420,
  }
];


export const valueFormatter = (item) => `${item.value}%`;
