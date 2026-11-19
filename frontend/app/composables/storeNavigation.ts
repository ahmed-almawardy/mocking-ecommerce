export interface MenuLink { key: string; category: string; search?: string }
export interface MenuGroup { title: string; items: MenuLink[] }
export interface MenuItem { key: string; category: string; groups: MenuGroup[] }

export const storeNavigation: MenuItem[] = [
  {
    key: 'cookers', category: 'Cookers', groups: [
      { title: 'menu.gasCookers', items: [
        { key: 'menu.gasCookers', category: 'Cookers', search: 'gas cooker' },
        { key: 'menu.freestandingCookers', category: 'Cookers', search: 'freestanding cooker' },
      ] },
      { title: 'menu.electricCookers', items: [
        { key: 'menu.electricCookers', category: 'Cookers', search: 'electric cooker' },
        { key: 'menu.builtInCookers', category: 'Cookers', search: 'built-in cooker' },
      ] },
    ],
  },
  {
    key: 'smallAppliances', category: 'Small Home Appliances', groups: [
      { title: 'menu.microwave', items: [
        { key: 'menu.convectionMicrowave', category: 'Small Home Appliances' },
        { key: 'menu.grillMicrowave', category: 'Small Home Appliances' },
        { key: 'menu.soloMicrowave', category: 'Small Home Appliances' },
      ] },
      { title: 'menu.electricOven', items: [{ key: 'menu.electricOven', category: 'Small Home Appliances' }] },
      { title: 'menu.vacuumCleaner', items: [
        { key: 'menu.baglessVacuum', category: 'Small Home Appliances' },
        { key: 'menu.vacuumWithBag', category: 'Small Home Appliances' },
      ] },
      { title: 'menu.clothesIron', items: [{ key: 'menu.clothesIron', category: 'Small Home Appliances' }] },
      { title: 'menu.heater', items: [{ key: 'menu.heater', category: 'Small Home Appliances' }] },
      { title: 'menu.waterAppliances', items: [
        { key: 'menu.waterDispenser', category: 'Small Home Appliances' },
        { key: 'menu.waterFilters', category: 'Small Home Appliances' },
        { key: 'menu.waterCooler', category: 'Small Home Appliances' },
        { key: 'menu.iceBox', category: 'Small Home Appliances' },
      ] },
      { title: 'menu.kitchenAppliances', items: [
        { key: 'menu.foodProcessor', category: 'Small Home Appliances' },
        { key: 'menu.handBlender', category: 'Small Home Appliances' },
        { key: 'menu.handMixer', category: 'Small Home Appliances' },
        { key: 'menu.electricGrill', category: 'Small Home Appliances' },
        { key: 'menu.kitchenMachine', category: 'Small Home Appliances' },
        { key: 'menu.kettle', category: 'Small Home Appliances' },
        { key: 'menu.blender', category: 'Small Home Appliances' },
        { key: 'menu.chopper', category: 'Small Home Appliances' },
        { key: 'menu.sandwichMaker', category: 'Small Home Appliances' },
        { key: 'menu.coffeeMachine', category: 'Small Home Appliances' },
      ] },
      { title: 'menu.waterHeaters', items: [
        { key: 'menu.electricWaterHeater', category: 'Small Home Appliances' },
        { key: 'menu.gasWaterHeater', category: 'Small Home Appliances' },
        { key: 'menu.instantWaterHeater', category: 'Small Home Appliances' },
      ] },
      { title: 'menu.fans', items: [
        { key: 'menu.standFans', category: 'Small Home Appliances' },
        { key: 'menu.wallFans', category: 'Small Home Appliances' },
        { key: 'menu.deskFans', category: 'Small Home Appliances' },
        { key: 'menu.ceilingFans', category: 'Small Home Appliances' },
        { key: 'menu.boxFans', category: 'Small Home Appliances' },
        { key: 'menu.ventilators', category: 'Small Home Appliances' },
      ] },
      { title: 'menu.airCooler', items: [{ key: 'menu.airCooler', category: 'Small Home Appliances' }] },
    ],
  },
  {
    key: 'televisions', category: 'Televisions', groups: [
      { title: 'menu.smartTvs', items: [{ key: 'menu.smartTvs', category: 'Televisions' }] },
      { title: 'menu.ledTvs', items: [{ key: 'menu.ledTvs', category: 'Televisions' }] },
      { title: 'menu.largeScreens', items: [{ key: 'menu.largeScreens', category: 'Televisions' }] },
    ],
  },
  {
    key: 'cooling', category: 'Cooling Appliances', groups: [
      { title: 'menu.refrigerators', items: [{ key: 'menu.refrigerators', category: 'Cooling Appliances' }] },
      { title: 'menu.freezers', items: [
        { key: 'menu.freezers', category: 'Cooling Appliances' },
        { key: 'menu.chestFreezers', category: 'Cooling Appliances' },
      ] },
    ],
  },
  {
    key: 'airConditioners', category: 'Air Conditioners', groups: [
      { title: 'menu.splitAc', items: [{ key: 'menu.splitAc', category: 'Air Conditioners' }] },
      { title: 'menu.inverterAc', items: [{ key: 'menu.inverterAc', category: 'Air Conditioners' }] },
      { title: 'menu.windowAc', items: [{ key: 'menu.windowAc', category: 'Air Conditioners' }] },
      { title: 'menu.portableAc', items: [{ key: 'menu.portableAc', category: 'Air Conditioners' }] },
    ],
  },
  {
    key: 'washingMachines', category: 'Washing Machines', groups: [
      { title: 'menu.frontLoad', items: [{ key: 'menu.frontLoad', category: 'Washing Machines' }] },
      { title: 'menu.topLoad', items: [{ key: 'menu.topLoad', category: 'Washing Machines' }] },
      { title: 'menu.dishwashers', items: [{ key: 'menu.dishwashers', category: 'Washing Machines' }] },
    ],
  },
]

