import { computed, onMounted, ref, watch } from 'vue';
type CalendarRef = {
  goPrev: () => void;
  goNext: () => void;
  changeView: (viewName: string) => void;
  gotoDate: (date: Date) => void;
  getCurrentView: () => string;
  getCurrentDate: () => Date | null;
} | null;

export function useCalendarHeader(calendarRef: { value: CalendarRef }) {
  const currentView = ref('timeGridWeek');
  const datePickerValue = ref<number | null>(null);

  const datePickerType = computed(() => {
    switch (currentView.value) {
      case 'dayGridMonth':
        return 'month';
      case 'timeGridWeek':
        return 'week';
      case 'timeGridDay':
        return 'date';
      default:
        return 'date';
    }
  });

  function syncCalendarHeader() {
    const currentDate = calendarRef.value?.getCurrentDate() ?? new Date();
    datePickerValue.value = currentDate.getTime();
  }

  function handleDatePick(value: number | null) {
    if (!value) {
      return;
    }
    calendarRef.value?.gotoDate(new Date(value));
    syncCalendarHeader();
  }

  const calendarActions = {
    prev: () => {
      calendarRef.value?.goPrev();
      syncCalendarHeader();
    },
    next: () => {
      calendarRef.value?.goNext();
      syncCalendarHeader();
    },
    view: (viewName: string) => {
      calendarRef.value?.changeView(viewName);
      currentView.value = viewName;
      syncCalendarHeader();
    },
  };

  watch(currentView, () => {
    syncCalendarHeader();
  });

  onMounted(() => {
    currentView.value = calendarRef.value?.getCurrentView() ?? 'timeGridWeek';
    syncCalendarHeader();
  });

  return {
    currentView,
    datePickerType,
    datePickerValue,
    handleDatePick,
    calendarActions,
  };
}
