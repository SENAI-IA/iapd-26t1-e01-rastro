export function semRepetir<Item>(lista: Item[]): Item[] {
  return [...new Set(lista)];
}
