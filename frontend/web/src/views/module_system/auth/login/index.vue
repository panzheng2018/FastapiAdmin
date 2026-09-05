<!-- 登录页：顶栏固定；仅插画列与表单区随布局切换 -->
<template>
  <div class="login-page-root flex h-screen w-full flex-col overflow-hidden" :style="loginBgStyle">
    <FaLoginCenterBackdrop v-if="panelAlign === 'center'" viewport-fixed />
    <FaAuthTopBar v-model:panel-align="panelAlign" />

    <div
      class="login-auth-split relative z-1 flex min-h-0 flex-1 overflow-hidden"
      :class="`login-auth-split--${panelAlign}`"
    >
      <div
        v-if="panelAlign !== 'center'"
        class="login-auth-split__col login-auth-split__col--illustration"
      >
        <FaLoginLeftView hide-top-branding />
      </div>

      <div
        class="login-auth-split__col login-auth-split__col--form login-page-panel relative flex min-h-0 min-w-0 flex-col"
        :class="panelAlign === 'center' ? 'bg-transparent' : 'bg-(--el-bg-color-page)'"
      >
        <div
          class="login-page-panel__main relative z-1 flex min-h-0 flex-1 flex-col overflow-hidden px-5 pb-2 pt-14 md:px-10 md:pt-18"
        >
          <ElScrollbar>
            <div
              class="login-page-panel__scroll pb-6"
              :class="panelAlign === 'center' && 'login-page-panel__scroll--centered'"
            >
              <div
                class="login-panel-align-row flex w-full items-center justify-center max-sm:min-h-0"
                :class="
                  panelAlign === 'center'
                    ? 'min-h-0 flex-1 py-4'
                    : 'min-h-[min(720px,calc(100vh-13rem))]'
                "
              >
                <div class="auth-right-wrap">
                  <div class="form">
                    <div class="form-intro">
                      <h3 class="title">{{ panelTitle }}</h3>
                      <p class="sub-title">{{ panelSubTitle }}</p>
                    </div>

                    <FaLoginAccountForm
                      ref="accountFormRef"
                      v-model:is-passing="isPassing"
                      v-model:is-click-pass="isClickPass"
                      v-model:login-form="loginForm"
                      :rules="rules"
                      :captcha-state="captchaState"
                      :code-loading="codeLoading"
                      :form-key="formKey"
                      :is-dark="isDark"
                      :drag-verify-text-color="dragVerifyTextColor"
                      :loading="loading"
                      @submit="handleSubmit"
                      @get-captcha="getCaptcha"
                    />
                  </div>
                </div>
              </div>
            </div>
          </ElScrollbar>
        </div>

        <footer
          class="login-page-footer login-page-footer--pinned shrink-0 pb-[max(0.75rem,env(safe-area-inset-bottom))] pt-3"
          :class="panelAlign === 'center' && 'login-page-footer--floating-layout'"
        >
          <div class="login-footer-text text-sm">
            <div class="login-footer-row">
              <a
                :href="configStore.configData?.git_code?.config_value || '#'"
                target="_blank"
                rel="noopener noreferrer"
                class="login-page-footer__link"
              >
                {{ configStore.configData?.copyright?.config_value || "" }}
              </a>
            </div>
            <span class="login-page-footer__sep login-footer-sep-center">|</span>
            <div class="login-footer-row">
              <a
                :href="configStore.configData?.help_doc?.config_value || '#'"
                target="_blank"
                rel="noopener noreferrer"
                class="login-page-footer__link"
              >
                帮助
              </a>
              <span class="login-page-footer__sep">|</span>
              <a
                :href="configStore.configData?.privacy?.config_value || '#'"
                target="_blank"
                rel="noopener noreferrer"
                class="login-page-footer__link"
              >
                隐私
              </a>
              <span class="login-page-footer__sep">|</span>
              <a
                :href="configStore.configData?.clause?.config_value || '#'"
                target="_blank"
                rel="noopener noreferrer"
                class="login-page-footer__link"
              >
                条款
              </a>
              <span
                v-if="configStore.configData?.keep_record?.config_value"
                class="login-page-footer__sep"
                >|</span
              >
              <span
                v-if="configStore.configData?.keep_record?.config_value"
                class="login-page-footer__record"
              >
                {{ configStore.configData.keep_record.config_value }}
              </span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { LocationQuery, RouteLocationRaw } from "vue-router";
import AuthAPI, {
  type CaptchaInfo,
  type LoginFormData,
} from "@/api/module_system/auth";

import { useConfigStore, useAppStore, useSettingsStore, useUserStore } from "@stores";
import { HttpError } from "@utils";
import { ElNotification } from "element-plus";
import type { FormRules } from "element-plus";
import { useLoginPanelAlign } from "./components/composables/useLoginPanelAlign";
import type FaLoginAccountForm from "./components/forms/FaLoginAccountForm.vue";

defineOptions({ name: "Login" });

const configStore = useConfigStore();
const settingStore = useSettingsStore();
const appStore = useAppStore();
const { isDark } = storeToRefs(settingStore);
const { t, locale } = useI18n();

const { panelAlign } = useLoginPanelAlign();

const panelTitle = computed(() => t("login.title"));
const panelSubTitle = computed(() => t("login.subTitle"));

const dragVerifyTextColor = computed(() =>
  isDark.value ? "rgba(255, 255, 255, 0.45)" : "var(--fa-gray-700)"
);
const formKey = ref(0);

watch(locale, () => {
  formKey.value++;
});

const userStore = useUserStore();
const router = useRouter();
const route = useRoute();
const isPassing = ref(false);
const isClickPass = ref(false);

const accountFormRef = ref<InstanceType<typeof FaLoginAccountForm> | null>(null);

const loading = ref(false);
const codeLoading = ref(false);

const loginForm = reactive<LoginFormData>({
  username: "",
  password: "",
  captcha_key: "",
  remember: true,
  login_type: "PC端",
});

// —— 登录页背景 ——
const loginBgStyle = computed(() => {
  const bg = configStore.configData?.login_bg?.config_value?.trim();
  return bg
    ? { backgroundImage: `url(${bg})`, backgroundSize: "cover", backgroundPosition: "center" }
    : {};
});

const captchaState = reactive<CaptchaInfo>({
  enable: false,
  key: "",
  img_base: "",
});

const rules = computed<FormRules>(() => {
  const base: FormRules = {
    username: [
      {
        required: true,
        trigger: "blur",
        message: t("login.message.username.required"),
      },
    ],
    password: [
      {
        required: true,
        trigger: "blur",
        message: t("login.message.password.required"),
      },
      {
        min: 6,
        message: t("login.message.password.min"),
        trigger: "blur",
      },
    ],
  };
  return base;
});

function setupAccount(key: AccountKey) {
  const selected = accounts.value.find((a: Account) => a.key === key);
  demoAccountKey.value = key;
  loginForm.username = selected?.username ?? "";
  loginForm.password = selected?.password ?? "";
}

async function getCaptcha() {
  try {
    codeLoading.value = true;
    const response = await AuthAPI.getCaptcha();
    const data = response.data.data;
    loginForm.captcha_key = data.key;
    captchaState.img_base = data.img_base;
    captchaState.enable = data.enable;
    // 重置滑块状态
    isPassing.value = false;
    isClickPass.value = false;
  } catch {
    captchaState.enable = false;
    loginForm.captcha_key = "";
  } finally {
    codeLoading.value = false;
  }
}

/** 滑块验证完成后通知后端标记 */
async function handleSliderPass(passed: boolean) {
  if (!passed || !loginForm.captcha_key) return;
  try {
    await AuthAPI.sliderComplete(loginForm.captcha_key);
  } catch {
    isPassing.value = false;
    await getCaptcha();
  }
}

/** 监听滑块通过状态 */
watch(isPassing, (val) => {
  handleSliderPass(val);
});

function resolveRedirectTarget(query: LocationQuery): RouteLocationRaw {
  const defaultPath = "/";
  const rawRedirect = (query.redirect as string) || defaultPath;
  try {
    const resolved = router.resolve(rawRedirect);
    return {
      path: resolved.path,
      query: resolved.query,
    };
  } catch {
    return { path: defaultPath };
  }
}

let notificationInstance: ReturnType<typeof ElNotification> | null = null;

const showVoteNotification = () => {
  // notificationInstance = ElNotification({
    // title: "⭐ FastapiAdmin 完全开源 · 期待您的 Star 支持 🙏",
    // message: `项目持续迭代中，若对您有所帮助，欢迎点亮 Star 支持！
    // <br/><a href="https://github.com/fastapiadmin/FastapiAdmin" target="_blank" style="color: var(--el-color-primary); text-decoration: none; font-weight: 500;">Github仓库 →</a>
    // <br/><a href="https://gitee.com/fastapiadmin/FastapiAdmin" target="_blank" style="color: var(--el-color-warning); text-decoration: none; font-weight: 500;">Gitee仓库 →</a>`,
    // type: "success",
    // position:
    //   panelAlign.value === "right" || panelAlign.value === "center"
    //     ? "bottom-left"
    //     : "bottom-right",
    // duration: 0,
    // dangerouslyUseHTMLString: true,
  // });
};

let voteTimer: ReturnType<typeof setTimeout> | null = null;

onMounted(async () => {
  await configStore.getConfig(true);
  if (userStore.isLogin) {
    await router.replace(resolveRedirectTarget(route.query));
    return;
  }
  getCaptcha();
  voteTimer = setTimeout(showVoteNotification, 500);
});

onActivated(() => {
  getCaptcha();
});

onBeforeUnmount(() => {
  if (voteTimer !== null) clearTimeout(voteTimer);
  notificationInstance?.close();
  notificationInstance = null;
});

watch(
  () => route.fullPath,
  () => {
    getCaptcha();
  }
);

const handleSubmit = async () => {
  if (!accountFormRef.value) return;

  try {
    const valid = await accountFormRef.value.validate?.();
    if (!valid) return;

    if (!isPassing.value) {
      isClickPass.value = true;
      return;
    }

    loading.value = true;

    await userStore.login(loginForm);
    await router.replace(resolveRedirectTarget(route.query));

    if (settingStore.showGuide) {
      appStore.showGuide(true);
    }
  } catch (error) {
    // 自增 formKey 强制重新挂载表单（滑块自动重置为初始状态）
    formKey.value++;
    await getCaptcha();
    if (!(error instanceof HttpError)) {
      console.error("[Login] Unexpected error:", error);
      ElNotification({
        title: "提示",
        message: error instanceof Error ? error.message : String(error),
        type: "error",
      });
    }
  } finally {
    loading.value = false;
  }
};
</script>
