import { computed, ref } from 'vue';

export function usePagination<T>(initialItems: T[] = [], pageSize = 10) {
  const items = ref<T[]>(initialItems);
  const currentPage = ref(0);

  const totalPages = computed(() => Math.max(1, Math.ceil(items.value.length / pageSize)));
  const pageItems = computed(() => {
    const start = currentPage.value * pageSize;
    return items.value.slice(start, start + pageSize);
  });

  function setItems(nextItems: T[]) {
    items.value = nextItems;
    currentPage.value = 0;
  }

  function canPrev() {
    return currentPage.value > 0;
  }

  function canNext() {
    return currentPage.value < totalPages.value - 1;
  }

  function prev() {
    if (canPrev()) {
      currentPage.value -= 1;
    }
  }

  function next() {
    if (canNext()) {
      currentPage.value += 1;
    }
  }

  return {
    items,
    currentPage,
    totalPages,
    pageItems,
    setItems,
    canPrev,
    canNext,
    prev,
    next,
  };
}
