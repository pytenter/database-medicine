import { reactive } from "vue";

export const appRequestState = reactive({
  pending: 0,
});

export const startRequest = () => {
  appRequestState.pending += 1;
};

export const finishRequest = () => {
  appRequestState.pending = Math.max(0, appRequestState.pending - 1);
};
